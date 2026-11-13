# Research Slides Library

A public library of HTML presentations about scientific research papers. The website provides search, sorting, and optional filters for browsing presentations. GitHub Actions automatically discovers slides and updates the catalog when changes are pushed to `main`.

## Add slides

1. In GitHub, navigate to `slides/` and choose **Add file → Create new file**.
2. Name the file `2026/new-paper/index.html` and paste your presentation HTML, replacing `2026` with the presentation year.
3. Add any images, stylesheets, scripts, or other assets inside `slides/2026/new-paper/`, using paths relative to `index.html`.
4. Commit to `main` (or merge your branch into `main`). After deployment, the presentation appears automatically; no catalog edits are needed.

For example:

```text
slides/2026/new-paper/
├── index.html
├── styles.css
└── assets/
    └── figure.png
```

The website lists presentations grouped by year, and the year is inferred from the first folder under `slides/`. The presentation title is read from the HTML `<title>` tag. If it is missing, the presentation folder name is used. Presentations can use any HTML framework and should be UTF-8 encoded. You can also add a standalone `.html` file directly inside `slides/`.

### Using Git

```sh
git clone https://github.com/AngeloFerrando/research-slides-library.git
cd research-slides-library
mkdir -p slides/2026/new-paper
# Copy index.html and any assets into slides/2026/new-paper/
git add slides/2026/new-paper
git commit -m "Add new paper presentation"
git push origin main
```

### Optional metadata

Add a `metadata.json` file beside `index.html` to provide extra information or override the year inferred from the folder. All fields are optional:

```json
{
  "title": "A shorter display title",
  "authors": ["A. Researcher", "B. Scientist"],
  "year": 2025,
  "description": "A concise summary of the presentation.",
  "tags": ["Machine learning", "Science"],
  "date": "2025-03-01"
}
```

The metadata title overrides the HTML title. `authors` can also be a string, `year` can be a number or string, and `tags` must be a list of strings. `date` is stored in the catalog but not displayed. Metadata is supported for presentation folders, not standalone files.
