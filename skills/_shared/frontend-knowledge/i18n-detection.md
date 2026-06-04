# i18n / Localization Detection

Framework-agnostic detection of a project's localization system, plus the universal rules any UI change must follow when one exists. Producer: `/implement` (detects, then applies). Consumer: `/verify` (checks compliance). If the project has **any** localization setup, missing translations = broken UX — treat it as a blocker.

## Detection strategy

1. **Search package.json, locale directories, and translation files:**
```bash
# Any i18n library in package.json
grep -E "i18n|intl|locale|translation|l10n|gettext|fluent" package.json 2>/dev/null

# Locale/translation directories
find . -maxdepth 3 -type d \( -name "locales" -o -name "locale" -o -name "i18n" -o -name "translations" -o -name "messages" -o -name "lang" -o -name "languages" \) 2>/dev/null

# Translation files
find . -maxdepth 4 -type f \( -name "*.po" -o -name "*.pot" -o -name "*.mo" -o -name "*.xliff" -o -name "*.arb" -o -name "**/en.json" -o -name "**/en-US.json" \) 2>/dev/null | head -10
```

2. **Check config files** for i18n setup: `next.config.*` (Next.js), `nuxt.config.*` (Nuxt), `angular.json` (Angular), `vue.config.*` / `vite.config.*` (Vue), `.env*` locale settings, any `i18n.*` config file.

3. **Grep for translation-function usage:**
```bash
grep -rE "useTranslations|useIntl|useT|t\(|i18n\.|formatMessage|gettext|__|_t\(|\$t\(|trans\(" src/ app/ components/ --include="*.ts" --include="*.tsx" --include="*.js" --include="*.vue" --include="*.svelte" 2>/dev/null | head -10
```

## If i18n detected — document the setup

- **Translation file location** — where locale files are stored
- **Supported locales** — which languages exist (e.g. `en`, `zh`, `es`)
- **Translation function** — how to call it (varies by framework; see table)
- **Key naming convention** — the pattern the project uses

## Universal rules

- **NO hardcoded user-facing strings** — all UI text uses the project's translation system
- **ALL locales updated** — new keys go in EVERY locale file, not just the default
- **Match existing patterns** — follow the project's key-naming convention
- **Handle plurals/interpolation** — use the framework's syntax for dynamic content

## Common frameworks reference

| Framework | Common Library | Translation Function |
|-----------|---------------|---------------------|
| React/Next.js | `next-intl`, `react-intl`, `i18next` | `t()`, `useTranslations()`, `formatMessage()` |
| Vue/Nuxt | `vue-i18n`, `@nuxtjs/i18n` | `$t()`, `t()` |
| Angular | `@angular/localize`, `ngx-translate` | `$localize`, `translate.instant()` |
| Svelte | `svelte-i18n` | `$_()`, `$t()` |
| Flutter | `flutter_localizations`, `intl` | `AppLocalizations.of(context)` |
| Python | `gettext`, `babel` | `_()`, `gettext()` |
| Go | `go-i18n` | `localizer.Localize()` |
| Ruby/Rails | `i18n` gem | `t()`, `I18n.t()` |

**Rule**: If the project has ANY localization setup, missing translations = broken UX. This is a blocker.
