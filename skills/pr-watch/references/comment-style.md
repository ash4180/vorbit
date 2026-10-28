# Comment style

Read this before you write any text for other readers. That means the PR comment, the approval text, and the Slack draft.

## Rules for all three

1. Write in first person. The text posts from the user's account.
2. Never mention Claude, an agent, a tool, or the user by name.
3. Use plain words. Sentences are 12 words or fewer. One idea each.
4. Never use a long dash. That means an em dash or an en dash. Use a comma, a period, or a colon.
5. Never choose "Request changes". Post a plain comment.
6. Thank the author first.
7. Small ideas go under "feel free to skip".
8. One comment per head commit. The monitor file's `Commented SHA` tells you if one exists.

## PR comment

Write it to a file in the run evidence folder. Use `{{image:1}}`, `{{image:2}}` where the pictures go. They match the order of `--images`.

Parts, in this order:

1. One line of thanks. Say what you tried or liked.
2. "One thing I noticed:" and one sentence that names the problem.
3. "To see it:" and numbered steps. Each step says who does what.
4. "Why it happens:" a short cause. Name the file only if you are sure.
5. "A possible fix, if you agree:" one or two lines.
6. "Before" with `{{image:1}}`: the problem on screen.
7. "After" with `{{image:2}}`: the same screen where it works. Use a real screenshot from QA. Never fake one.
8. "Feel free to skip:" small ideas. Leave this out if you have none.

Example:

```markdown
Thank you for this PR. The new highlight works well for single words.

One thing I noticed: a space at the end of the search turns off some highlights.

To see it:
1. Open an incident chat that has the word "test".
2. Type "test " in the search box, with a space at the end.
3. Look at the matches in the messages.

Why it happens: the search text is not trimmed before it is matched.

A possible fix, if you agree: trim the search text first.

Before:
{{image:1}}

After:
{{image:2}}

Feel free to skip: the story could show a long search term too.
```

## Approval text

Short and soft. Two to four sentences.

1. Say it looks good, and thank the author.
2. Say what you tested and on which commit.
3. Say what stayed "Not done" and why, when something did. For example: "I could not test Korean text. Dev has no Korean chat data."

## Slack draft

Write it as the user. One to three short sentences.

1. Say the PR number and that you approved it.
2. Say what stayed untested, when something did.
3. Link the PR.

Never send it. Save it with the draft tool. Tell the user it is waiting.
