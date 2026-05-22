# Edge Case Catalog

Common edge cases organized by category. Use this catalog to cross-reference discovered cases and identify any missed scenarios.

---

## Input & Validation Edge Cases

### Text Fields
| Edge Case | Test Scenario | Expected Behavior |
|-----------|---------------|-------------------|
| Empty string | Submit with just spaces | Trim and validate as empty |
| Max length | Paste text exceeding limit | Truncate or block at limit |
| Min length | Submit 1 char when 3 required | Show min length error |
| Unicode | Submit 日本語, العربية, עברית | Handle correctly, check display |
| Emojis | Include 😀 in text | Handle encoding, check display width |
| HTML tags | Submit `<script>alert('xss')</script>` | Escape or strip tags |
| SQL injection | Submit `'; DROP TABLE users;--` | Parameterized queries, no injection |
| Very long word | Submit 500 char word no spaces | Word wrap or truncate properly |
| Leading/trailing spaces | "  text  " | Trim on submit |
| Newlines | Multi-line in single-line field | Strip or convert to spaces |
| Zero-width chars | Invisible characters | Strip or handle |
| RTL text | Right-to-left languages | Proper text direction |

### Numeric Fields
| Edge Case | Test Scenario | Expected Behavior |
|-----------|---------------|-------------------|
| Zero | Enter 0 | Valid unless explicitly disallowed |
| Negative | Enter -5 | Valid or show "positive only" error |
| Decimal | Enter 3.14159 | Handle precision, round if needed |
| Very large | Enter 999999999999 | Handle overflow, show max limit |
| Scientific notation | Enter 1e10 | Convert or reject |
| Leading zeros | Enter 007 | Strip or preserve based on context |
| Thousand separators | Enter 1,000 | Parse correctly |
| Currency symbols | Enter $100 | Strip symbol or reject |

### Date/Time Fields
| Edge Case | Test Scenario | Expected Behavior |
|-----------|---------------|-------------------|
| Leap year | Feb 29, 2024 | Valid |
| Invalid leap year | Feb 29, 2023 | Invalid date error |
| End of month | Jan 31 → Feb (no 31st) | Handle gracefully |
| Past date | Yesterday when future required | Show "future date required" |
| Far future | Year 2099 | Validate or warn |
| Far past | Year 1900 | Validate or warn |
| Timezone change | Schedule across DST boundary | Handle 2am DST gap |
| Midnight | 00:00 vs 24:00 | Normalize to 00:00 |
| Date format | MM/DD vs DD/MM | Use locale or clarify |

### File Uploads
| Edge Case | Test Scenario | Expected Behavior |
|-----------|---------------|-------------------|
| Zero-byte file | Upload empty file | Reject or warn |
| Max size | Upload over limit | Show size limit error |
| Wrong type | Upload .exe when expecting .pdf | Show file type error |
| Duplicate name | Upload same filename twice | Rename or confirm overwrite |
| Special chars in name | `file (1).pdf`, `file#name.pdf` | Handle or sanitize |
| Very long filename | 255+ character filename | Truncate preserving extension |
| No extension | File with no extension | Detect type from content |
| Corrupted file | Upload damaged image | Show corruption error |
| Slow upload | Large file on slow connection | Show progress, allow cancel |

---

## State & Data Edge Cases

### Empty States
| Scenario | Context | Expected Behavior |
|----------|---------|-------------------|
| First run | Brand new user, no data | Show onboarding/getting started |
| Filtered empty | Search returns nothing | "No results for X", suggest alternatives |
| Deleted all | User deleted all items | Different from first run - show "create new" |
| Permission empty | No access to any items | Explain why empty, how to get access |
| Loading empty | Still loading, appears empty | Show loading state, not empty state |

### List Boundaries
| Scenario | Count | Expected Behavior |
|----------|-------|-------------------|
| Single item | 1 | Show without pagination |
| Page boundary | Exactly 25 (page size) | Don't show "next" if no more |
| Large list | 10,000+ items | Paginate, virtualize, or limit |
| Zero items | 0 | Show empty state |
| Odd number | 7 in 3-column grid | Handle incomplete row |

### Data Freshness
| Scenario | Context | Expected Behavior |
|----------|---------|-------------------|
| Stale data | Cache older than threshold | Show refresh option or auto-refresh |
| Real-time update | Another user changed data | Update UI or show notification |
| Version conflict | Edit based on old version | Conflict resolution UI |
| Deleted while viewing | Item deleted by another user | Redirect with message |
| Schema change | API response has new/missing fields | Handle gracefully, no crash |

---

## Network & System Edge Cases

### Network Conditions
| Scenario | Condition | Expected Behavior |
|----------|-----------|-------------------|
| Offline | No network | Show offline indicator, disable network features |
| Slow network | 3G/Edge connection | Show loading states, don't timeout prematurely |
| Intermittent | Connection dropping | Retry with backoff, preserve state |
| Online resume | Reconnect after offline | Sync pending changes, refresh data |

### API Responses
| Scenario | Response | Expected Behavior |
|----------|----------|-------------------|
| 200 Success | Normal response | Process and display |
| 201 Created | Resource created | Navigate or show success |
| 204 No Content | Empty success | Handle empty body |
| 400 Bad Request | Validation failed | Show field-specific errors |
| 401 Unauthorized | Not logged in | Redirect to login |
| 403 Forbidden | No permission | Show permission denied |
| 404 Not Found | Resource missing | Show not found, offer navigation |
| 409 Conflict | Version mismatch | Show conflict resolution |
| 429 Rate Limited | Too many requests | Show rate limit message, retry after |
| 500 Server Error | Server failure | Show generic error, retry option |
| 502/503/504 | Gateway/service issues | Show temporary error, auto-retry |
| Timeout | No response | Show timeout error, retry option |
| Malformed JSON | Invalid response | Handle parse error gracefully |

### Partial Failures
| Scenario | Context | Expected Behavior |
|----------|---------|-------------------|
| Batch partial | 3 of 5 items fail | Show which failed, allow retry |
| Dependent fail | Step 2 of 3 fails | Rollback step 1 or allow continue |
| Background fail | Async job fails | Notify user, offer retry |

---

## Authentication & Session Edge Cases

### Session States
| Scenario | Context | Expected Behavior |
|----------|---------|-------------------|
| Session expired | Token expired mid-use | Prompt re-auth, preserve state |
| Concurrent logout | Logged out in another tab | Redirect to login |
| Password changed | Password changed elsewhere | Force re-auth |
| Account disabled | Admin disabled account | Show account disabled message |
| Multiple sessions | Same user, multiple devices | Allow or limit based on policy |

### Authentication Flows
| Scenario | Context | Expected Behavior |
|----------|---------|-------------------|
| SSO redirect | Redirect to identity provider | Handle return URL properly |
| MFA required | Need second factor | Show MFA prompt |
| MFA timeout | Took too long for MFA | Restart flow |
| OAuth cancel | User cancels OAuth flow | Return to login gracefully |
| Social auth fail | Google/Facebook auth fails | Show error, offer alternatives |

---

## Concurrent & Multi-User Edge Cases

### Simultaneous Actions
| Scenario | Context | Expected Behavior |
|----------|---------|-------------------|
| Double click | User clicks submit twice | Disable button, deduplicate |
| Double submit | Form submitted twice | Idempotent handling, one result |
| Race condition | Two updates near-simultaneous | Last-write-wins or conflict UI |
| Stale update | Edit based on old data | Detect version, prompt refresh |

### Multi-Tab Behavior
| Scenario | Context | Expected Behavior |
|----------|---------|-------------------|
| Logout in tab | Log out in one tab | Log out all tabs |
| Edit in tab | Edit same item in two tabs | Warn or sync |
| Cart sync | Add to cart in multiple tabs | Sync cart state |
| State conflict | Different states in tabs | Resolve or show warning |

---

## Device & Browser Edge Cases

### Responsive Breakpoints
| Scenario | Width | Expected Behavior |
|----------|-------|-------------------|
| Mobile small | 320px | Everything fits, touch-friendly |
| Mobile standard | 375px | Standard mobile layout |
| Tablet | 768px | Hybrid layout |
| Desktop small | 1024px | Desktop layout, no horizontal scroll |
| Desktop wide | 1920px+ | Max-width container or fluid |

### Browser Behaviors
| Scenario | Browser | Expected Behavior |
|----------|---------|-------------------|
| Back button | After form submit | Warn about resubmit or handle |
| Forward | After back navigation | Restore state properly |
| Refresh | During unsaved work | Warn or auto-save |
| Browser close | Tab/window close | Warn about unsaved work |
| Print | Ctrl+P | Print-friendly layout |
| Zoom | 200% zoom | No horizontal scroll, readable |

### Input Methods
| Scenario | Method | Expected Behavior |
|----------|--------|-------------------|
| Keyboard only | Tab navigation | Full functionality accessible |
| Touch only | No hover states | Touch targets sufficient size |
| Voice input | Dictation | Accept natural language |
| Paste | Paste formatted text | Strip formatting or preserve |
| Autofill | Browser autofill | Accept and validate |

---

## Accessibility Edge Cases

### Assistive Technology
| Scenario | Tool | Expected Behavior |
|----------|------|-------------------|
| Screen reader | VoiceOver/NVDA | All content announced properly |
| Focus visible | Keyboard navigation | Clear focus indicators |
| Skip links | Screen reader | Skip to main content available |
| Form labels | Screen reader | All inputs labeled properly |
| Error announcement | Screen reader | Errors announced when they appear |
| Dynamic content | Screen reader | Live regions for updates |

### Visual Accommodations
| Scenario | Setting | Expected Behavior |
|----------|---------|-------------------|
| High contrast | Windows high contrast | Visible in all modes |
| Reduced motion | Prefer reduced motion | No animations |
| Large text | 200% font scaling | No text truncation, readable |
| Color blindness | Deuteranopia, Protanopia | Not color-dependent information |

---

## Time-Based Edge Cases

### Timezone Handling
| Scenario | Context | Expected Behavior |
|----------|---------|-------------------|
| User timezone | Display date/time | Use user's local timezone |
| Server timezone | Stored timestamps | Store in UTC |
| Cross-timezone | User travels | Update to new timezone |
| DST boundary | Schedule during DST change | Handle ambiguous/skipped times |

### Scheduling Edge Cases
| Scenario | Context | Expected Behavior |
|----------|---------|-------------------|
| Schedule past | Try to schedule 5 minutes ago | Reject or execute immediately |
| Schedule far | Schedule 2 years out | Allow or set reasonable limit |
| Recurring end | Recurring event end date | Handle series end gracefully |
| Recurring conflict | Recurring event hits holiday | Skip or notify |

---

## Business Logic Edge Cases

### Pricing & Currency
| Scenario | Context | Expected Behavior |
|----------|---------|-------------------|
| Zero price | Free item | Display "Free" not "$0.00" |
| Fraction cents | $1.999 | Round appropriately |
| Currency change | User changes currency | Recalculate or show conversion |
| Negative amount | Refund or credit | Display clearly as credit |

### Inventory & Limits
| Scenario | Context | Expected Behavior |
|----------|---------|-------------------|
| Out of stock | During checkout | Show unavailable, offer alternatives |
| Low stock | Only 2 left | Show warning |
| Over-purchase | Try to buy more than available | Limit to available |
| Quota exceeded | Hit usage limit | Show limit, offer upgrade |

---

## Security Edge Cases

### Input Sanitization
| Attack Vector | Input | Expected Behavior |
|--------------|-------|-------------------|
| XSS | `<script>` tags | Escape or strip |
| SQL Injection | `'; DROP TABLE` | Parameterized queries |
| Path traversal | `../../etc/passwd` | Validate paths |
| CSRF | Cross-site form submit | CSRF tokens |

### Rate Limiting
| Scenario | Context | Expected Behavior |
|----------|---------|-------------------|
| Login attempts | 5 failed logins | Lock out temporarily |
| API abuse | 1000 requests/minute | Return 429, show limit |
| Form spam | Rapid form submits | Debounce, CAPTCHA |
