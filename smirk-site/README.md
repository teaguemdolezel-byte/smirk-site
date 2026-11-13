# Smirk site

Static site for smirk.io. No framework: `build.py` assembles everything into `dist/`. Vercel (project `smirk-io`) runs the build on every commit, using the settings in `vercel.json`.

## Layout

- `src/home.html` — the home page. The notes list is filled in at build time.
- `src/work-together.html` — the "Wanna work together?" page and its two forms.
- `content/notes/*.md` — one file per Thinking in Systems note.
- `static/` — favicon, share image, robots.txt.
- `vercel.json` — tells Vercel how to build and where the output is.
- `build.py` — builds `dist/`: home, work-together, `/thinking` index, one page per note, sitemap.

## Add a note

1. Copy any file in `content/notes/` and rename it, e.g. `06-your-slug.md`.
2. Edit the header:

   ```
   ---
   title: Your title
   slug: your-slug            (address becomes smirk.io/thinking/your-slug)
   number: 06
   date: 2026-12-01
   excerpt: One or two sentences for lists and link previews.
   quote: The one line worth remembering (blue handwriting, mid-note).
   rule: The closing takeaway, shown under "One rule".
   draft: false               (true keeps it on the site but hidden from search engines)
   topic: Operations          (optional; becomes a filter on the read-all page)
   ---
   ```

3. Write the note below the header in two parts, with a line of `***` between them:
   the setup (1 to 3 paragraphs), then the turn (1 to 3 paragraphs). The blue quote is
   placed where the `***` is, and the rule closes the note. Every note has the same layout.
4. Commit the file to the `main` branch on GitHub. Vercel runs `python3 build.py` and publishes the result to smirk.io automatically. No promote step.

To preview locally instead: `python3 build.py`, then open the files in `dist/`.

The home page shows the newest five notes; `/thinking` shows all of them. Notes are ordered by date, newest first.

## Forms

Both forms on the work-together page send through FormSubmit to teague@dolezel.com. The address appears twice in `src/work-together.html`.
