# Gaston Security — website

Live: https://gaston-security.com/ · QR short link: https://gaston-security.com/scan → `/?utm_source=qr`

Plain HTML/CSS/JS, hosted on Cloudflare Workers (static assets), deployed automatically from the `main` branch of this repo.

## Edit the site

| Want to change… | Edit this |
|---|---|
| Wording, phone, email, hours, services | `index.html` (search for the text) |
| Colors, spacing, fonts | `style.css` — tokens at the top |
| Where the QR code lands | `_redirects` — the `/scan` line. Reprint nothing. |
| Form email key / photo upload settings | `index.html` (`access_key`) and `script.js` (`CONFIG`) |
| Logo | the inline SVG at the top of `index.html`; then rerun `python3 tools/render.py` for `og.png` and the touch icon |

## Redeploy

Every push to `main` deploys in about 30 seconds.

**From the GitHub website (no tools needed):** open the file on github.com → pencil icon → edit → "Commit changes".

**From a computer:**
```
git pull
# edit files
git add -A && git commit -m "Update hours" && git push
```
Watch the deploy at Cloudflare dashboard → Workers & Pages → gaston-security-site → Deployments.
A bad deploy can be rolled back there in one click ("Rollback to this deployment").

## Form submissions

- Delivered by **Web3Forms** (free tier, 250/month) to the email set in the Web3Forms dashboard.
- Spam protection: hidden honeypot field + hCaptcha ("I am human" box).
- Optional photo and a backup copy of every submission go to Supabase if `CONFIG` in `script.js` is filled in.
- Text alerts: in Gmail/Yahoo, create a filter for emails with subject "Service request from gaston-security.com" that forwards to your carrier's email-to-SMS address (e.g. `9017309691@vtext.com` for Verizon, `@txt.att.net` for AT&T, `@tmomail.net` for T-Mobile).

## QR codes

`qr/` holds print-ready files. Regenerate (and self-test) with:
```
python3 tools/make_qr.py https://gaston-security.com/scan
```
- `qr-card.*` — 1 in, business cards
- `qr-sticker.*` — 3 in, doors and the van
- `qr-plain.*` — bare code for anything else

Print the SVGs when you can (sharp at any size); the PNGs are 300 dpi.
