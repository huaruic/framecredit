# Triage Labels

| Label in mattpocock/skills | Label in our tracker | Meaning |
| --- | --- | --- |
| `needs-triage` | `needs-triage` | Maintainer needs to evaluate this issue |
| `needs-info` | `needs-info` | Waiting on reporter for more information |
| `ready-for-agent` | `ready-for-agent` | Fully specified, ready for an AFK agent |
| `ready-for-human` | `ready-for-human` | Requires human implementation |
| `wontfix` | `wontfix` | Will not be actioned |

When a skill mentions a canonical role, use the corresponding label string from this table.

## Project-local terminal state

| Label in our tracker | Meaning |
| --- | --- |
| `completed` | Every acceptance criterion has been verified against actual behavior |

`completed` is a FrameCredit-local addition with no canonical counterpart in
mattpocock/skills. Set `Status: completed` only after all acceptance criteria
have been verified against the actual behavior of the code — through tests,
real runs, or inspected output media — not against intent or memory. Check an
acceptance box only when its criterion has been verified that way; leave
unverified boxes unchecked even on otherwise finished work. When later work
supersedes details of a completed issue, record the supersession as a comment
under `## Comments` instead of unchecking boxes or reopening the issue.
