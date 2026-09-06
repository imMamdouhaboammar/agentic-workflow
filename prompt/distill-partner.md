# Distill Partner - Essence Extraction & Optimization

A command to discuss: Extracting core essence → Removing unnecessary items → Identifying automation opportunities → Reducing token usage/time.

---

## 🚀 How to Use

```bash
/distill-partner "Description of current task or plan" , ".file"
```

---

## 🔄 Interview Flow (4 Steps)

## Process

1. **File Analysis**: Understand current state (role, length, structure)
2. **Console Multiple-Choice Question Loop**:
  - Questions: Format as text, console, numbered lists, presenting 4 multiple-choice questions per turn.
  - Present 4 questions per turn
  - Repeat until user terminates with "done", "end", "none", etc.
  - Collect concrete improvement proposals for each area
3. **Organize Improvement Plan**: Consolidate all collected improvements and formulate an execution plan

---

### **Step 1: Understand Context**

Summarize and confirm the information provided by the user (or current conversation).

```
To summarize what you've shared:
• [Key Content Summary]
• [Goal]
• [Current State]

In this context, let's think together: "What can we eliminate, and what can we automate?"
```

---

### **Step 2: Q1 - Extract Core Essence**

> "What do you consider the **absolute core essentials** in this plan/task?"

**Answer Format**: Freeform input (1-3 items)

**Next Step**: Await user response

---

### **Step 3: Q2 - Remove Unnecessary Items**

> "What are the items that are **not strictly necessary or can be excluded**?"

**Answer Format**: Freeform input (bullet points)

**Next Step**: Await user response

---

### **Step 4: Q3 - Identify Automation Opportunities**

> "Which parts are **repetitive or can be automated**?"
>
> Example: Document generation, file sorting, data cleanup, logging, etc.

**Answer Format**: Freeform input (task names)

**Next Step**: Await user response

---

### **Step 5: Q4 - Token & Time Reduction**

> "Are there ways to **reduce tokens or shorten execution time using scripts or automation**?"
>
> Example: Automated template generation, automated document formatting, boilerplate automation, etc.

**Answer Format**: Freeform input

**Next Step**: Proceed to Step 6 after collecting all responses

---

### **Step 6: Present Distilled Results**

After completing all interviews:

```
✨ Distilled Results

🎯 Core Essence (Keep):
  • [Reflecting Q1 answers]

🗑️ Candidates for Removal (Safe to skip):
  • [Reflecting Q2 answers]

⚙️ Automation Opportunities:
  • [Q3 answers] → Implementable via scripts
  • [Q4 answers] → Token reduction strategies

💻 Pseudocode (Automation Logic):
  if task == "repetitive":
      → Write script (Python/Bash)
  if task == "document generation":
      → Template + automation
  if task == "data processing":
      → Batch script

📌 Next Steps:
  → Implement automation items first
  → Focus exclusively on the core essence
  → Exclude unnecessary parts
```

---

## 💡 When to Use

- ✅ When writing a Task definition and wondering "Do we really need all of this?"
- ✅ When a design plan is overly complex
- ✅ When considering "Should we reduce the scope?" before implementation
- ✅ When general discussion needs structuring: "Let's organize this"
- ✅ When discussing token reduction strategies

---

## 🎯 Goals of this Command

✅ **A. Extract Essence**
- Clarify: "What is the core?"

✅ **B. Minimize Scope**
- Verify: "Can we safely eliminate non-essentials?"

✅ **C. Identify Automation Opportunities**
- Discover: "Where can we apply automation?"

✅ **D. Maximize Efficiency**
- Discuss: "How do we minimize tokens and time?"

---

## 📝 Key Characteristics

- **Versatile**: Usable across any stage and scenario
- **Sequential Progression**: One-by-one dialogue via AskUserQuestion
- **Concise**: Delivers results using bullet points + pseudocode
- **Automation-Centric**: Sharp focus on "Which parts can be scripted?"
