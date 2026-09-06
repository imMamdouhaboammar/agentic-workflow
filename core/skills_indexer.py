#!/usr/bin/env python3
"""
skills_indexer.py — Agentic Skills Mesh & Universal Auto-Indexer

Implements:
1. Multi-path Auto-Discovery across local user environments (~/.gemini, ~/.claude, ~/.agents, ~/.agent-kernel, workspace)
2. Semantic Agentic Node Extraction:
   - Types: skill, workflow, agent, playbook, rule, guard
   - Metadata: id, name, version, author, description, tags
   - Triggers: slash commands, intent keywords, file patterns
   - Execution: tools required, rules & guards, graph edges (links)
3. Dual-Format Synchronized Indexing:
   - skills-index.json: Full typed graph representation
   - skills-index.toon: High-density Token-Optimized Object Notation for LLM context injection (~65% token savings)
4. Runtime Skills Mesh & Intent Resolver for Autopilot and Coding Agents.
"""

import os
import sys
import json
import re
import time
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Set, Tuple, Any


class NodeType(str, Enum):
    SKILL = "skill"
    WORKFLOW = "workflow"
    AGENT = "agent"
    PLAYBOOK = "playbook"
    RULE = "rule"
    GUARD = "guard"


@dataclass
class AgenticNode:
    id: str
    name: str
    type: NodeType
    path: str
    description: str = ""
    version: str = "1.0.0"
    author: str = ""
    tags: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)
    tools_required: List[str] = field(default_factory=list)
    rules_and_guards: List[str] = field(default_factory=list)
    edges: List[str] = field(default_factory=list)  # Related or dependent node IDs
    source_dir: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["type"] = self.type.value
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgenticNode":
        data_copy = dict(data)
        if "type" in data_copy and isinstance(data_copy["type"], str):
            try:
                data_copy["type"] = NodeType(data_copy["type"])
            except ValueError:
                data_copy["type"] = NodeType.SKILL
        return cls(**data_copy)


class FrontmatterParser:
    """Extracts and parses YAML or JSON frontmatter and markdown sections."""

    @staticmethod
    def parse_markdown(content: str) -> Tuple[Dict[str, Any], str]:
        frontmatter: Dict[str, Any] = {}
        body = content

        # Match YAML frontmatter between ---
        yaml_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        if yaml_match:
            raw_yaml = yaml_match.group(1)
            body = yaml_match.group(2)
            for line in raw_yaml.split("\n"):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip().strip("\"'")
                    if val.startswith("[") and val.endswith("]"):
                        # Simple list parse
                        items = [x.strip().strip("\"'") for x in val[1:-1].split(",") if x.strip()]
                        frontmatter[key] = items
                    else:
                        frontmatter[key] = val

        return frontmatter, body


class NodeClassifier:
    """Classifies a skill into an Agentic Node type based on semantics and naming."""

    GUARD_PATTERNS = ["guard", "security", "protect", "block", "secret-filter", "safety", "tdd"]
    WORKFLOW_PATTERNS = ["workflow", "pipeline", "orchestrat", "gsd-", "phase", "loop", "lifecycle"]
    AGENT_PATTERNS = ["agency-", "engineer", "specialist", "architect", "reviewer", "tester", "guardian", "developer", "lead"]
    PLAYBOOK_PATTERNS = ["playbook", "guide", "handbook", "best-practice", "convention", "patterns", "how-to"]
    RULE_PATTERNS = ["rule", "constitution", "invariant", "directive", "governance", "standard"]

    @classmethod
    def classify(cls, node_id: str, name: str, description: str, body: str) -> NodeType:
        text = f"{node_id} {name} {description}".lower()

        for g in cls.GUARD_PATTERNS:
            if g in text:
                return NodeType.GUARD

        for r in cls.RULE_PATTERNS:
            if r in text and ("must" in body.lower() or "never" in body.lower() or "rule" in text):
                return NodeType.RULE

        for a in cls.AGENT_PATTERNS:
            if a in text or node_id.startswith("agency-"):
                return NodeType.AGENT

        for w in cls.WORKFLOW_PATTERNS:
            if w in text or node_id.startswith("gsd-"):
                return NodeType.WORKFLOW

        for p in cls.PLAYBOOK_PATTERNS:
            if p in text or "step 1" in body.lower() or "procedure" in body.lower():
                return NodeType.PLAYBOOK

        return NodeType.SKILL


class TriggerExtractor:
    """Extracts slash commands, trigger keywords, and tool requirements."""

    SLASH_CMD_RE = re.compile(r"(/(?:[a-zA-Z0-9_\-]+))")
    TOOL_RE = re.compile(r"\b(view_file|write_to_file|replace_file_content|run_command|read_url_content|search_web|find_by_name|grep_search|list_dir|ask_question|generate_image|bash)\b", re.IGNORECASE)

    @classmethod
    def extract_triggers(cls, node_id: str, name: str, description: str, body: str, tags: List[str]) -> List[str]:
        triggers: Set[str] = set()

        # Add node id and words from name
        triggers.add(node_id.lower())
        for word in re.split(r"[\s\-_]+", name.lower()):
            if len(word) > 2 and word not in ["the", "and", "for", "with", "app"]:
                triggers.add(word)

        # Add tags
        for t in tags:
            triggers.add(t.lower())

        # Slash commands mentioned in text
        slash_cmds = cls.SLASH_CMD_RE.findall(body[:2000])
        for sc in slash_cmds:
            if len(sc) > 2 and not sc.startswith("/Users") and not sc.startswith("/var"):
                triggers.add(sc.lower())

        # Keywords from description
        desc_words = re.split(r"[\s\-_,.:;]+", description.lower())
        for w in desc_words:
            if len(w) > 3 and w not in ["this", "that", "with", "when", "using", "from"]:
                triggers.add(w)

        return sorted(list(triggers))[:15]

    @classmethod
    def extract_tools(cls, body: str) -> List[str]:
        matches = cls.TOOL_RE.findall(body)
        unique_tools = set()
        for m in matches:
            norm = m.lower()
            if norm == "bash":
                norm = "run_command"
            unique_tools.add(norm)
        return sorted(list(unique_tools))


class EdgeResolver:
    """Discovers relationships, prerequisites, and complementary links between nodes."""

    COMPLEMENTARY_MAP = {
        "omni-skill": ["skill-conductor", "skill-architect", "skill-portability-compiler", "skill-evaluator", "agentic-workflow"],
        "agentic-workflow": ["omni-skill", "workflow-generator", "clean-code-guard", "fable-tdd"],
        "test-driven-development": ["test-guard", "clean-code-guard", "fable-tdd"],
        "fable-tdd": ["test-guard", "clean-code-guard", "test-driven-development"],
        "clean-code-guard": ["test-guard", "autoreview"],
        "workflow-generator": ["gsd-plan-phase", "architecture-guardian"],
        "agency-senior-developer": ["agency-code-reviewer", "agency-reality-checker", "clean-code-guard"],
        "agency-code-reviewer": ["agency-reality-checker", "clean-code-guard", "test-guard"],
        "agency-api-tester": ["test-guard", "clean-code-guard"],
    }

    @classmethod
    def resolve_edges(cls, node_id: str, all_node_ids: Set[str], body: str) -> List[str]:
        edges: Set[str] = set()

        # Check pre-defined complementaries
        if node_id in cls.COMPLEMENTARY_MAP:
            for c in cls.COMPLEMENTARY_MAP[node_id]:
                if c in all_node_ids:
                    edges.add(c)

        # Check body text mentions of other skill IDs
        for other_id in all_node_ids:
            if other_id != node_id and len(other_id) > 4:
                if other_id in body:
                    edges.add(other_id)

        # Prefix clustering (e.g. gsd-* or fable-* or 21st-*)
        prefix = node_id.split("-")[0] if "-" in node_id else ""
        if prefix in ["gsd", "fable", "agency", "ce"]:
            related_in_cluster = [
                n for n in all_node_ids
                if n.startswith(prefix + "-") and n != node_id
            ]
            for r in related_in_cluster[:3]:
                edges.add(r)

        return sorted(list(edges))[:8]


class ToonFormatter:
    """
    Token-Optimized Object Notation (TOON) Serializer.
    
    A compact, human-readable, token-dense serialization format that cuts LLM
    context token cost by ~65% compared to JSON.
    """

    @staticmethod
    def format_node(node: AgenticNode) -> str:
        tools_str = ",".join(sorted(node.tools_required)) if node.tools_required else "none"
        triggers_str = ",".join(sorted(node.triggers[:8])) if node.triggers else ""
        links_str = ",".join(sorted(node.edges)) if node.edges else ""
        rules_str = ",".join(sorted(node.rules_and_guards)) if node.rules_and_guards else ""

        lines = [
            f"@node:{node.id} [type:{node.type.value}, name:\"{node.name}\", tools:{tools_str}]",
            f"path:{node.path}",
            f"summary:{node.description.strip()}"
        ]
        if triggers_str:
            lines.append(f"triggers:{triggers_str}")
        if links_str:
            lines.append(f"links:{links_str}")
        if rules_str:
            lines.append(f"rules:{rules_str}")

        return "\n".join(lines)

    @classmethod
    def serialize_mesh(cls, nodes: List[AgenticNode]) -> str:
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        header = [
            f"# ════════════════════════════════════════════════════════════════",
            f"# AGENTIC SKILLS MESH — TOKEN-OPTIMIZED OBJECT NOTATION (TOON)",
            f"# Generated: {timestamp} | Active Nodes: {len(nodes)}",
            f"# ════════════════════════════════════════════════════════════════\n"
        ]
        body_blocks = [cls.format_node(n) for n in nodes]
        return "\n".join(header) + "\n\n".join(body_blocks) + "\n"

    @classmethod
    def parse_toon(cls, content: str) -> List[Dict[str, Any]]:
        """Parses a TOON file back into node dictionaries."""
        nodes: List[Dict[str, Any]] = []
        current: Dict[str, Any] = {}

        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("@node:"):
                if current and "id" in current:
                    nodes.append(current)
                current = {"id": "", "name": "", "type": "skill", "tools_required": [], "triggers": [], "edges": [], "rules_and_guards": []}
                # Parse header: @node:<id> [type:<type>, name:"<name>", tools:<tools>]
                match = re.match(r"^@node:([^\s\[]+)(?:\s*\[(.*)\])?", line)
                if match:
                    current["id"] = match.group(1)
                    attrs = match.group(2)
                    if attrs:
                        # Split by comma only when followed by a key:
                        for part in re.split(r",\s*(?=[a-zA-Z_]+:)", attrs):
                            if ":" in part:
                                k, v = part.split(":", 1)
                                k = k.strip()
                                v = v.strip().strip("\"'")
                                if k == "type":
                                    current["type"] = v
                                elif k == "name":
                                    current["name"] = v
                                elif k == "tools":
                                    current["tools_required"] = [x.strip() for x in v.split(",") if x.strip() and x.strip() != "none"]

            elif current:
                if line.startswith("path:"):
                    current["path"] = line.split("path:", 1)[1].strip()
                elif line.startswith("summary:"):
                    current["description"] = line.split("summary:", 1)[1].strip()
                elif line.startswith("triggers:"):
                    current["triggers"] = [x.strip() for x in line.split("triggers:", 1)[1].split(",") if x.strip()]
                elif line.startswith("links:"):
                    current["edges"] = [x.strip() for x in line.split("links:", 1)[1].split(",") if x.strip()]
                elif line.startswith("rules:"):
                    current["rules_and_guards"] = [x.strip() for x in line.split("rules:", 1)[1].split(",") if x.strip()]

        if current and "id" in current:
            nodes.append(current)

        return nodes


class SkillScanner:
    """Discovers and scans all skills directories across the system and project."""

    def __init__(self, project_dir: str = ".", candidate_dirs: Optional[List[str]] = None):
        self.project_dir = os.path.abspath(project_dir)
        self.explicit_candidate_dirs = [os.path.abspath(d) for d in candidate_dirs] if candidate_dirs is not None else None

    def get_candidate_directories(self) -> List[str]:
        """Returns ordered list of directories to scan for skills."""
        if self.explicit_candidate_dirs is not None:
            return self.explicit_candidate_dirs

        dirs: List[str] = []

        # 1. Environment variable overrides
        env_paths = os.getenv("AGENT_SKILLS_PATH", "") or os.getenv("GEMINI_SKILLS_PATH", "")
        if env_paths:
            for p in re.split(r"[:;]", env_paths):
                if p and os.path.isdir(p):
                    dirs.append(os.path.abspath(p))

        if os.getenv("AGENT_SKILLS_ISOLATED") == "1":
            return dirs

        # 2. User Home Skill Directories
        home = os.path.expanduser("~")
        global_candidates = [
            os.path.join(home, ".gemini", "config", "skills"),
            os.path.join(home, ".gemini", "config", "plugins"),
            os.path.join(home, ".claude", "skills"),
            os.path.join(home, ".agents", "skills"),
            os.path.join(home, ".agent-kernel", "skills"),
            os.path.join(home, ".agent-kernel"),
        ]
        for gc in global_candidates:
            if os.path.isdir(gc):
                dirs.append(os.path.abspath(gc))

        # 3. Project Workspace Directories
        local_candidates = [
            os.path.join(self.project_dir, ".claude", "skills"),
            os.path.join(self.project_dir, ".cursor", "skills"),
            os.path.join(self.project_dir, ".gemini", "skills"),
            os.path.join(self.project_dir, ".gemini", "config", "skills"),
            os.path.join(self.project_dir, ".agents", "skills"),
            os.path.join(self.project_dir, "skills"),
        ]
        for lc in local_candidates:
            if os.path.isdir(lc):
                dirs.append(os.path.abspath(lc))

        # Deduplicate while preserving order
        seen = set()
        deduped = []
        for d in dirs:
            if d not in seen:
                seen.add(d)
                deduped.append(d)

        return deduped

    def scan_directory(self, target_dir: str) -> List[Tuple[str, str]]:
        """
        Scans a directory for skill files (SKILL.md, .skills.json, README.md).
        Returns list of (skill_dir_path, main_skill_file_path).
        """
        results: List[Tuple[str, str]] = []
        if not os.path.isdir(target_dir):
            return results

        try:
            entries = os.listdir(target_dir)
        except (PermissionError, OSError):
            return results

        # Check if target_dir itself is a skill directory (has SKILL.md or .skills.json)
        self_skill_md = os.path.join(target_dir, "SKILL.md")
        if os.path.isfile(self_skill_md):
            results.append((target_dir, self_skill_md))

        # Check direct subdirectories
        for entry in sorted(entries):
            if entry.startswith(".") or entry in ["node_modules", "dist", "build", "__pycache__"]:
                continue
            entry_path = os.path.join(target_dir, entry)
            if os.path.isdir(entry_path):
                skill_file = None
                for fname in ["SKILL.md", "skill.md", "README.md"]:
                    candidate = os.path.join(entry_path, fname)
                    if os.path.isfile(candidate):
                        skill_file = candidate
                        break
                if skill_file:
                    results.append((entry_path, skill_file))
                else:
                    # Check 1 level deeper for plugin structures like plugins/firebase/skills/abc
                    try:
                        sub_entries = os.listdir(entry_path)
                        for sub in sub_entries:
                            sub_path = os.path.join(entry_path, sub)
                            if os.path.isdir(sub_path):
                                sub_skill = os.path.join(sub_path, "SKILL.md")
                                if os.path.isfile(sub_skill):
                                    results.append((sub_path, sub_skill))
                    except (PermissionError, OSError) as e:
                        import logging
                        logging.warning("skills_indexer: cannot scan %s: %s", entry_path, e)

        return results


class AgenticSkillsMesh:
    """
    Universal Agentic Skills Mesh and Auto-Indexer.
    
    Acts as the single source of discovery, graph modeling, and resolution
    for skills, workflows, agents, playbooks, and rules across the system.
    """

    def __init__(self, project_dir: str = ".", candidate_dirs: Optional[List[str]] = None):
        self.project_dir = os.path.abspath(project_dir)
        self.scanner = SkillScanner(self.project_dir, candidate_dirs=candidate_dirs)
        self.nodes: Dict[str, AgenticNode] = {}
        self.json_index_path = os.path.join(self.project_dir, "skills-index.json")
        self.toon_index_path = os.path.join(self.project_dir, "skills-index.toon")

    def scan(self) -> Dict[str, AgenticNode]:
        """Discovers, parses, and resolves all skills across the system."""
        candidate_dirs = self.scanner.get_candidate_directories()
        discovered_skills: List[Tuple[str, str, str]] = []  # (source_dir, skill_dir, file_path)

        for cdir in candidate_dirs:
            found = self.scanner.scan_directory(cdir)
            for skill_dir, file_path in found:
                discovered_skills.append((cdir, skill_dir, file_path))

        # Check project root SKILL.md
        root_skill = os.path.join(self.project_dir, "SKILL.md")
        if os.path.isfile(root_skill):
            discovered_skills.append((self.project_dir, self.project_dir, root_skill))

        temp_nodes: Dict[str, Tuple[AgenticNode, str]] = {}
        all_ids: Set[str] = set()

        for source_dir, skill_dir, file_path in discovered_skills:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(100_000)  # Read first 100k bytes max
            except Exception:
                continue

            frontmatter, body = FrontmatterParser.parse_markdown(content)

            # Determine ID
            node_id = frontmatter.get("name")
            if not node_id:
                node_id = os.path.basename(skill_dir)
            node_id = re.sub(r"[^a-zA-Z0-9_\-]+", "-", node_id.strip()).lower().strip("-")
            if not node_id:
                node_id = f"skill-{len(temp_nodes)}"

            name = frontmatter.get("name", os.path.basename(skill_dir))
            description = frontmatter.get("description", "")
            if not description:
                # Extract first meaningful paragraph from body
                for line in body.split("\n"):
                    line = line.strip()
                    if line and not line.startswith("#") and not line.startswith("-") and len(line) > 20:
                        description = line[:200]
                        break
                if not description:
                    description = f"Autonomous agentic skill {name}"

            version = str(frontmatter.get("version", "1.0.0"))
            author = str(frontmatter.get("author", ""))
            tags = frontmatter.get("tags", [])
            if isinstance(tags, str):
                tags = [tags]

            node_type = NodeClassifier.classify(node_id, name, description, body)
            triggers = TriggerExtractor.extract_triggers(node_id, name, description, body, tags)
            tools = TriggerExtractor.extract_tools(body)

            rules: List[str] = []
            if node_type in [NodeType.GUARD, NodeType.RULE]:
                rules.append(f"enforce-{node_id}")
            if "tdd" in node_id or "test" in node_id:
                rules.append("enforce-tdd-verification")
            if "clean-code" in node_id:
                rules.append("enforce-clean-code-solid")

            node = AgenticNode(
                id=node_id,
                name=name,
                type=node_type,
                path=file_path,
                description=description,
                version=version,
                author=author,
                tags=tags,
                triggers=triggers,
                tools_required=tools,
                rules_and_guards=rules,
                edges=[],
                source_dir=source_dir
            )
            temp_nodes[node_id] = (node, body)
            all_ids.add(node_id)

        # Second pass: resolve edges across all discovered nodes
        resolved_nodes: Dict[str, AgenticNode] = {}
        for nid, (node, body) in temp_nodes.items():
            node.edges = EdgeResolver.resolve_edges(nid, all_ids, body)
            resolved_nodes[nid] = node

        self.nodes = resolved_nodes
        return self.nodes

    def build_index(self, output_dir: Optional[str] = None) -> Tuple[str, str]:
        """
        Compiles and writes skills-index.json and skills-index.toon.
        Returns paths to both files.
        """
        if not self.nodes:
            self.scan()

        target_dir = os.path.abspath(output_dir) if output_dir else self.project_dir
        os.makedirs(target_dir, exist_ok=True)

        json_path = os.path.join(target_dir, "skills-index.json")
        toon_path = os.path.join(target_dir, "skills-index.toon")

        # 1. Write JSON index
        nodes_list = sorted(list(self.nodes.values()), key=lambda n: n.id)
        index_payload = {
            "version": "1.0.0",
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_nodes": len(nodes_list),
            "stats": {
                "skills": sum(1 for n in nodes_list if n.type == NodeType.SKILL),
                "workflows": sum(1 for n in nodes_list if n.type == NodeType.WORKFLOW),
                "agents": sum(1 for n in nodes_list if n.type == NodeType.AGENT),
                "playbooks": sum(1 for n in nodes_list if n.type == NodeType.PLAYBOOK),
                "rules": sum(1 for n in nodes_list if n.type == NodeType.RULE),
                "guards": sum(1 for n in nodes_list if n.type == NodeType.GUARD),
            },
            "nodes": [n.to_dict() for n in nodes_list]
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(index_payload, f, indent=2)

        # 2. Write TOON index (high-density compact format)
        toon_content = ToonFormatter.serialize_mesh(nodes_list)
        with open(toon_path, "w", encoding="utf-8") as f:
            f.write(toon_content)

        self.json_index_path = json_path
        self.toon_index_path = toon_path
        return json_path, toon_path

    def load_index(self) -> bool:
        """Loads index from skills-index.json if it exists."""
        if os.path.isfile(self.json_index_path):
            try:
                with open(self.json_index_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    nodes_data = data.get("nodes", [])
                    self.nodes = {d["id"]: AgenticNode.from_dict(d) for d in nodes_data}
                    return True
            except Exception as e:
                import logging
                logging.warning("skills_indexer: failed to load index from %s: %s", self.json_index_path, e)
        return False

    def get_node(self, node_id: str) -> Optional[AgenticNode]:
        """Retrieves an agentic node by its unique ID."""
        if not self.nodes:
            if not self.load_index():
                self.scan()
        return self.nodes.get(node_id)

    def search(self, query: str, limit: int = 10) -> List[AgenticNode]:
        """Fast keyword search across all indexed nodes."""
        if not self.nodes:
            if not self.load_index():
                self.scan()

        q_terms = [t.lower() for t in re.split(r"[\s\-_]+", query.strip()) if t]
        if not q_terms:
            return list(self.nodes.values())[:limit]

        scored: List[Tuple[int, AgenticNode]] = []
        for node in self.nodes.values():
            score = 0
            node_text = f"{node.id} {node.name} {node.description} {' '.join(node.tags)} {' '.join(node.triggers)}".lower()

            for term in q_terms:
                if term == node.id:
                    score += 20
                elif term in node.name.lower():
                    score += 10
                elif term in node.triggers:
                    score += 5
                elif term in node_text:
                    score += 2

            if score > 0:
                scored.append((score, node))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [node for _, node in scored[:limit]]

    def resolve_for_intent(self, intent: str, active_files: Optional[List[str]] = None, top_k: int = 5) -> List[AgenticNode]:
        """
        Agentic Intent Resolver:
        Maps a user task, prompt, or stage description to the most appropriate
        Agentic Nodes, specialized Agents, Playbooks, and Governance Guards.
        """
        candidates = self.search(intent, limit=top_k * 2)
        if not candidates:
            return []

        selected: List[AgenticNode] = []
        seen_ids: Set[str] = set()

        # Prioritize guards if intent implies testing, modification, or code changes
        intent_lower = intent.lower()
        needs_code_guard = any(w in intent_lower for w in ["write", "code", "implement", "refactor", "fix", "feature"])
        needs_test_guard = any(w in intent_lower for w in ["test", "verify", "qa", "assert", "spec"])

        if needs_code_guard:
            for g_id in ["clean-code-guard", "autoreview"]:
                if g_id in self.nodes and g_id not in seen_ids:
                    selected.append(self.nodes[g_id])
                    seen_ids.add(g_id)

        if needs_test_guard:
            for t_id in ["test-guard", "test-driven-development", "fable-tdd"]:
                if t_id in self.nodes and t_id not in seen_ids:
                    selected.append(self.nodes[t_id])
                    seen_ids.add(t_id)

        for c in candidates:
            if c.id not in seen_ids and len(selected) < top_k:
                selected.append(c)
                seen_ids.add(c.id)

        return selected

    def get_toon_context(self, node_ids: Optional[List[str]] = None) -> str:
        """
        Produces high-density TOON context string ready for LLM prompt injection.
        """
        if not self.nodes:
            if not self.load_index():
                self.scan()

        target_nodes: List[AgenticNode] = []
        if node_ids:
            for nid in node_ids:
                if nid in self.nodes:
                    target_nodes.append(self.nodes[nid])
        else:
            target_nodes = list(self.nodes.values())

        return ToonFormatter.serialize_mesh(target_nodes)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Agentic Skills Mesh & Universal Indexer")
    parser.add_argument("command", choices=["scan", "index", "search", "resolve", "toon"], help="Command to run")
    parser.add_argument("query", nargs="?", default="", help="Search query or intent")
    parser.add_argument("--output", "-o", default=".", help="Output directory for index files")
    parser.add_argument("--limit", "-n", type=int, default=10, help="Max results limit")

    args = parser.parse_args()
    mesh = AgenticSkillsMesh()

    if args.command == "scan":
        print("🔍 Scanning skills directories across user environment...")
        nodes = mesh.scan()
        print(f"✅ Discovered {len(nodes)} agentic nodes across:")
        for d in mesh.scanner.get_candidate_directories():
            print(f"   - {d}")

    elif args.command == "index":
        print(f"⚡ Building synchronized JSON and TOON skills indexes in '{args.output}'...")
        json_file, toon_file = mesh.build_index(output_dir=args.output)
        json_sz = os.path.getsize(json_file)
        toon_sz = os.path.getsize(toon_file)
        saving = max(0, int((1.0 - (toon_sz / json_sz)) * 100)) if json_sz > 0 else 0
        print(f"✅ Indexed {len(mesh.nodes)} Agentic Nodes:")
        print(f"   📄 JSON: {json_file} ({json_sz:,} bytes)")
        print(f"   ⚡ TOON: {toon_file} ({toon_sz:,} bytes) -> [{saving}% token/size savings]")

    elif args.command == "search":
        results = mesh.search(args.query, limit=args.limit)
        print(f"🔎 Found {len(results)} matches for '{args.query}':")
        for r in results:
            print(f"   [{r.type.value.upper()}] {r.id}: {r.name} — {r.description[:80]}...")

    elif args.command == "resolve":
        results = mesh.resolve_for_intent(args.query, top_k=args.limit)
        print(f"🎯 Resolved {len(results)} agentic node(s) for task: '{args.query}':")
        for r in results:
            print(f"   [{r.type.value.upper()}] {r.id} ({r.path})")
            if r.triggers:
                print(f"       Triggers: {', '.join(r.triggers[:5])}")
            if r.edges:
                print(f"       Links: {', '.join(r.edges[:5])}")

    elif args.command == "toon":
        node = mesh.get_node(args.query)
        if node:
            print(ToonFormatter.format_node(node))
        else:
            print(f"❌ Node '{args.query}' not found.")
            sys.exit(1)


if __name__ == "__main__":
    main()
