import re
import sys
from html import escape


class TMLSiteGenerator:
    def __init__(self):
        self.title = "TMLSite"
        self.body = []
        self.in_features = False

    def load(self, filename):
        with open(filename, "r") as file:
            lines = [
                line.strip()
                for line in file.readlines()
                if line.strip() and not line.strip().startswith("#")
            ]

        for line in lines:
            if line.startswith("site "):
                self.close_features()
                self.title = self.get_string(line)

            elif line.startswith("section "):
                self.close_features()
                self.body.append(f"<h2>{escape(self.get_string(line))}</h2>")

            elif line.startswith("text "):
                self.close_features()
                self.body.append(f"<p>{escape(self.get_string(line))}</p>")

            elif line.startswith("feature "):
                if not self.in_features:
                    self.body.append("<ul>")
                    self.in_features = True
                self.body.append(f"<li>{escape(self.get_string(line))}</li>")

            elif line.startswith("code "):
                self.close_features()
                self.body.append(f"<pre><code>{escape(self.get_string(line))}</code></pre>")

            elif line.startswith("link "):
                self.close_features()
                match = re.match(r'link "(.+)" "(.+)"', line)
                if not match:
                    raise ValueError(f"Invalid link line: {line}")
                label, url = match.groups()
                self.body.append(f'<p><a href="{escape(url)}">{escape(label)}</a></p>')

        self.close_features()

    def close_features(self):
        if self.in_features:
            self.body.append("</ul>")
            self.in_features = False

    def generate(self, output_file="index.html"):
        body_html = "\n".join(self.body)

        html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>{escape(self.title)}</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      max-width: 850px;
      margin: 40px auto;
      padding: 20px;
      line-height: 1.6;
      background: #111827;
      color: #f9fafb;
    }}

    h1, h2 {{
      color: #93c5fd;
    }}

    pre {{
      background: #020617;
      padding: 16px;
      border-radius: 8px;
      overflow-x: auto;
    }}

    code {{
      color: #facc15;
    }}

    a {{
      color: #38bdf8;
    }}

    .card {{
      background: #1f2937;
      padding: 24px;
      border-radius: 14px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.35);
    }}
  </style>
</head>
<body>
  <div class="card">
    <h1>{escape(self.title)}</h1>
    {body_html}
  </div>
</body>
</html>
"""

        with open(output_file, "w") as file:
            file.write(html)

        print(f"Website generated: {output_file}")

    def get_string(self, line):
        match = re.search(r'"(.+)"', line)
        if not match:
            raise ValueError(f"Expected quoted string in line: {line}")
        return match.group(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python tmlsite_generator.py website.tmlsite")
        return

    generator = TMLSiteGenerator()
    generator.load(sys.argv[1])
    generator.generate()


if __name__ == "__main__":
    main()