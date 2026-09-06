#!/usr/bin/env python3
"""
agentic_workflow.cli — Python Console Script Entry Point for AgenticWorkflow
"""

import sys
import os
import argparse
import subprocess

from core.autopilot_engine import AutopilotEngine
from core.clean_code_guard import run_guard_report
from core.skills_indexer import AgenticSkillsMesh as SkillsIndexer
from core.hooks import HookDispatcher
from core.integrations import IntegrationInstaller, LifecycleDirector

def main():
    parser = argparse.ArgumentParser(
        prog="agentic-workflow",
        description="⚡ AgenticWorkflow CLI — Universal Autonomous Agentic Toolchain ⚡"
    )
    parser.add_argument("--version", "-v", action="version", version="agentic-workflow 1.2.2")

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Autopilot
    auto_parser = subparsers.add_parser("autopilot", aliases=["run", "drive"], help="Run autonomous autopilot workflow")
    auto_parser.add_argument("--title", default="Autonomous Production Workflow", help="Project title")
    auto_parser.add_argument("--goal", default="Autonomous end-to-end execution without user bottleneck", help="Goal")

    # Guard
    guard_parser = subparsers.add_parser("guard", aliases=["clean-code"], help="Run Clean Code Guard pass")
    guard_parser.add_argument("target", nargs="?", default=".", help="Target directory")

    # Skills
    skills_parser = subparsers.add_parser("skills", aliases=["skills-mesh"], help="Agentic skills mesh and indexer")
    skills_parser.add_argument("action", choices=["scan", "index", "search", "resolve", "toon"], help="Skills action")
    skills_parser.add_argument("query", nargs="?", default="", help="Query or intent")
    skills_parser.add_argument("--output", default=".", help="Output directory for index")

    # Integrations
    int_parser = subparsers.add_parser("integrations", aliases=["tools"], help="Supportive tools & lifecycle director")
    int_parser.add_argument("action", choices=["status", "install", "provision", "list", "phase", "director", "add"], nargs="?", default="status")
    int_parser.add_argument("target", nargs="?", default="all", help="Target tool, phase, or repo")

    # Hooks
    hook_parser = subparsers.add_parser("hooks", aliases=["uahf"], help="Universal Agentic Hooks Framework")
    hook_parser.add_argument("action", choices=["status", "install", "dispatch", "session-end"], nargs="?", default="status")
    hook_parser.add_argument("--command", dest="cmd_arg", help="Command to evaluate")
    hook_parser.add_argument("--agent", dest="agent_arg", default="default_agent", help="Agent ID")
    hook_parser.add_argument("--reason", dest="reason_arg", default="manual_exit", help="Exit reason")

    # Status
    subparsers.add_parser("status", help="Query live workflow dashboard")

    # Test
    subparsers.add_parser("test", help="Run automated test suite")

    # Engine
    engine_parser = subparsers.add_parser("engine", help="Run event-driven workflow engine")
    engine_parser.add_argument("--runtime", choices=["py", "ts"], default="py", help="Engine runtime")

    # Parse arguments
    args, unknown = parser.parse_known_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    if args.command in ["autopilot", "run", "drive"]:
        print(f"🚀 [agentic-workflow] Launching Autopilot Engine...")
        print(f"   Title: \"{args.title}\"")
        print(f"   Goal:  \"{args.goal}\"")
        engine = AutopilotEngine(project_dir=root_dir, auto_approve=True)
        engine.plan_default_workflow(title=args.title, goal=args.goal)
        success = engine.run_all()
        sys.exit(0 if success else 1)

    elif args.command in ["guard", "clean-code"]:
        exit_code = run_guard_report(args.target)
        sys.exit(exit_code)

    elif args.command in ["skills", "skills-mesh"]:
        indexer = SkillsIndexer(project_dir=root_dir)
        if args.action == "scan":
            skills = indexer.scan_environment()
            print(f"Found {len(skills)} agentic skills across environment.")
        elif args.action == "index":
            res = indexer.build_indices(output_dir=args.output)
            print(f"✅ Synchronized indices built at: {args.output}")
        elif args.action == "search":
            results = indexer.search(args.query)
            print(f"Found {len(results)} matches for '{args.query}':")
            for r in results:
                print(f"  - {r.name} ({r.path})")
        elif args.action == "resolve":
            nodes = indexer.resolve_intent(args.query)
            print(f"Resolved {len(nodes)} agentic nodes for intent '{args.query}':")
            for n in nodes:
                print(f"  - {n.name} [{n.type}]")

    elif args.command in ["integrations", "tools"]:
        installer = IntegrationInstaller(project_dir=root_dir)
        if args.action == "status":
            results = installer.check_all()
            for r in results:
                print(f"  - {r.name}: [{'ONLINE' if r.installed else 'MISSING'}] {r.details}")
        elif args.action in ["install", "provision"]:
            results = installer.provision_all()
            for r in results:
                print(f"  ✓ {r.name}: {r.status} ({len(r.locations)} targets)")
        elif args.action in ["phase", "director"]:
            ld = LifecycleDirector(project_dir=root_dir)
            dirs = ld.get_phase_directives(args.target if args.target != "all" else "planning")
            print(f"Active Tools: {', '.join(dirs.active_integrations)}")
            print(dirs.system_prompt_overlay)

    elif args.command in ["hooks", "uahf"]:
        dispatcher = HookDispatcher(project_dir=root_dir)
        if args.action == "status":
            import json
            print(json.dumps(dispatcher.get_status(), indent=2))
        elif args.action == "session-end":
            from core.hooks.session_end import SessionEndManager
            m = SessionEndManager(project_dir=root_dir)
            res = m.handle_session_end(agent_id=args.agent_arg, reason=args.reason_arg)
            print(f"✅ {res.message}")

    elif args.command == "status":
        subprocess.run(["python3", ".claude/hooks/scripts/query_workflow.py", "--project-dir", root_dir, "--dashboard"])

    elif args.command == "test":
        # Run tests
        subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"], cwd=root_dir)

    elif args.command == "engine":
        from core.engine_py.runner import main as run_engine
        import asyncio
        asyncio.run(run_engine())

if __name__ == "__main__":
    main()
