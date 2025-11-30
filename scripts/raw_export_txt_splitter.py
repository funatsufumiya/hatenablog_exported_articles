import argparse
import json
import sys
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("path", help="path to raw_export.txt")
    parser.add_argument("-o", "--output", help="output directory")
    parser.add_argument("-j", "--json", action='store_true', help="export as json (to stdout)")
    args = parser.parse_args()

    global articles
    articles = []

    with open(args.path, encoding='utf-8') as f:
        lines = f.read().splitlines()
        # print(lines[0:10])

        global article, bodies, is_header
        article = {}
        bodies = []
        is_header = True

        def finalize_article():
            global articles, article, bodies, is_header
            is_header = True
            article["body"] = '\n'.join(bodies)
            articles.append(article)
            article = {}

        for line in lines:
            if line == "-----":
                if is_header:
                    is_header = False
                    bodies = []
                else:
                    finalize_article()
            elif line == "--------":
                pass
                # just ignore
            elif line.startswith("BODY:"):
                is_header = False
                # and ignore
            elif is_header:
                lst = line.split(': ')
                key = lst[0].lower()
                value = ""
                if len(lst) > 1:
                    value = lst[1]

                article[key] = value
            elif not is_header:
                # if line.endswith("\n"):
                #     line = line[0:-1]
                bodies.append(line)
            else:
                raise "unreachable"
            
        if "title" in article and "body" in article:
            finalize_article()

    if args.json:
        obj = {"count": len(articles), "articles": articles}
        s = json.dumps(obj, ensure_ascii=False, indent=2)
        print(s)
        sys.exit()

    print(f"count: {len(articles)}")

    # print(articles[0])

    out_dir: str = args.output

    if os.path.exists(out_dir):
        os.removedirs(out_dir)

    os.makedirs(out_dir)

    sp = os.sep

    for article in articles:
        if "title" in article and "body" in article and "basename" in article:
            basename: str = article["basename"]
            id = basename.replace('/','-')
            title: str = article["title"]
            # print(f"title: {title}")
            dir = out_dir + sp + id
            os.makedirs(dir)
            body = article["body"]
            del article["body"]
            header = article
            header_json_str = json.dumps(header, ensure_ascii=False, indent=2)
            with open(dir + sp + "content.html", "w", encoding='utf-8') as f:
                f.write(body)
            with open(dir + sp + "headers.json", "w", encoding='utf-8') as f:
                f.write(header_json_str)
