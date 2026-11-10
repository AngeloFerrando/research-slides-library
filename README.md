# Research Slides Library

A public, static library of independent HTML presentations. GitHub Actions discovers presentations on every push to `main`, creates a catalog, and publishes the website and slide files to GitHub Pages. Nothing needs to be registered by hand.

## Enable deployment

1. Create a **public** repository named `research-slides-library` and push these files to its `main` branch.
2. In the repository, open **Settings → Pages → Build and deployment** and select **GitHub Actions** as the source.
3. Open **Actions → Deploy to GitHub Pages** and use **Run workflow** on `main` if the initial push ran before Pages was configured. Future pushes to `main` deploy automatically.
4. Open the URL shown in the deployment job or on the Pages settings page. For a standard user project site it is `https://<github-username>.github.io/research-slides-library/`. DNS or a first deployment can take a few minutes.

GitHub Pages and Actions are available for public repositories on GitHub Free; no server or database is needed. The site and all files under `website/` and `slides/` are public. Do not upload private material, credentials, or unpublished research.

## Add a presentation on GitHub

1. Open the repository on GitHub and navigate to `slides/`.
2. Choose **Add file → Create new file**, enter `new-paper/index.html` as the filename, paste your complete HTML, and commit directly to `main` (or merge your branch into `main`).
3. For assets, open `slides/new-paper/`, choose **Add file → Upload files**, and upload your files. Create subfolders as needed; alternatively upload the folder from Git. Use paths relative to `index.html`, such as `assets/figure.png`.
4. After the Actions deployment finishes, the presentation appears automatically. Its title comes from the HTML `<title>` tag. No metadata or catalog changes are required.

For example:

```text
slides/new-paper/
├── index.html
├── assets/figure.png
└── styles.css
```

```html
<title>A New Paper</title>
<link rel="stylesheet" href="styles.css">
<img src="assets/figure.png" alt="Experimental results">
```

You can also put a standalone `.html` file directly inside `slides/`. Each folder's `index.html` is a separate presentation; nested folders inside it are treated as assets, not separate presentations. Files are served unchanged; use your preferred presentation framework. If a framework relies on external resources, those resources must be accessible to visitors.

## Add using Git

```sh
git clone https://github.com/<github-username>/research-slides-library.git
cd research-slides-library
mkdir -p slides/new-paper/assets
# Copy index.html and assets into slides/new-paper/
git add slides/new-paper
git commit -m "Add new paper presentation"
git push origin main
```

## Optional metadata

Place `metadata.json` beside a folder's `index.html` to enrich its card. Every field is optional:

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

`authors` may also be a string; `year` may be a number or string; `tags` must be a list of strings. Metadata title overrides the HTML title. If neither is present, the folder name is used with hyphens and underscores converted to spaces. `date` is stored in the catalog for future use; the current interface does not display it. Invalid JSON or invalid field types stop the build with an error identifying the file. Standalone HTML files use their title or filename and do not support metadata.

## Remove or rename

Delete the entire presentation folder, or rename it and commit the change. The next deployment rebuilds the catalog and replaces the published site, removing old cards and files. When renaming through GitHub, move **all** assets as well as `index.html`. External links to the old URL will no longer work.

## Local preview and tests

With Python 3 installed, from the repository root:

```sh
python3 -m unittest discover -s tests -v
mkdir -p _site
cp -a website/. _site/
cp -a slides _site/slides
python3 scripts/generate_catalog.py --output _site/catalog.json
python3 -m http.server 8000 --directory _site
```

Visit `http://localhost:8000/`. Use a local HTTP server rather than opening `index.html` directly, because browsers restrict fetching the catalog from `file:` URLs. Rebuild `_site` from scratch when testing removals or renames; Actions starts with a fresh build directory. The output uses relative links and works both at the domain root and under a project subpath.

## Troubleshooting

- **No site or failed deployment:** check **Settings → Pages** is set to **GitHub Actions**, then inspect the failed run in **Actions**. Ensure Actions are enabled and Pages is available for the public repository. If an environment protection rule requires approval, approve the deployment.
- **Presentation missing:** ensure the folder is directly inside `slides/`, its entry point is named exactly `index.html`, and changes reached `main`. Check that the latest deployment succeeded; it can take a few minutes to propagate.
- **Build fails on metadata:** inspect the Actions log for the filename and validation error. Fix or remove its optional `metadata.json` and push again. Presentation HTML must be UTF-8.
- **Broken images or scripts:** confirm assets were committed and the paths and capitalization match exactly. Use relative URLs, not root-relative paths such as `/assets/...`, which point outside the project subpath.
- **Old files or cards:** check the latest `main` deployment has completed and refresh the browser. The generated artifact contains only `website/`, `slides/`, and the generated catalog; it is not a permanent branch of accumulated files.

The workflow only reads repository contents and requests the GitHub Pages and OIDC permissions needed for deployment. Repository collaborators with write access manage the source; visitors need no account.
