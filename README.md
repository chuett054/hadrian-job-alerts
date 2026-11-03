# Hadrian Job Alerts

Checks [Hadrian's job board](https://jobs.ashbyhq.com/hadrian-automation) every 6 hours and emails me when a new role fits my filters.

## How it works

1. A GitHub Actions workflow pulls every open role from Hadrian's public Ashby API.
2. `check_jobs.py` filters the roles using `config.json` and skips anything in `seen.json`.
3. New matches go into a GitHub issue that @mentions the repo owner, and GitHub emails the owner about it.
4. The workflow commits the notified role IDs to `seen.json`, so each role only alerts once.

## Filters

Edit `config.json` to change what matches:

| Setting | Current behavior |
| --- | --- |
| `title_include` | Product manager, product owner, APM, and technical program manager titles |
| `title_exclude` | Senior, staff, principal, lead, director, and other senior titles |
| `early_career_titles` | Intern, new grad, associate, and "All Levels" titles skip the experience check |
| `max_required_years` | Other roles match if their description asks for 2 years or fewer, or states no requirement |

All locations are included.

## Run it

Run the tests:

```bash
python3 -m unittest
```

Run a check now:

```bash
gh workflow run check-jobs.yml
```

## Email setup

Emails depend on your GitHub notification settings. Under [Notifications](https://github.com/settings/notifications), keep email turned on for participating activity and @mentions.
