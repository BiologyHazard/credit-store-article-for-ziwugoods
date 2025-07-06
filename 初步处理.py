from bs4 import BeautifulSoup


with open("【子午谷工作室】信用交易所购买策略_20250704_200610.html", "r", encoding="utf-8") as file:
    content = file.read()

soup = BeautifulSoup(content, "html.parser")

# 删除 <style> 标签
for style in soup.find_all("style"):
    style.decompose()

head = soup.head
if head:
    # 直接插入KaTeX相关标签和本地style.css
    katex_tags = '''
    <!-- KaTeX -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/katex.min.css"
        integrity="sha384-5TcZemv2l/9On385z///+d7MSYlvIEw9FuZTIdZ14vJLqWphw7e7ZPuOiCHJcFCP" crossorigin="anonymous" />
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/katex.min.js"
        integrity="sha384-cMkvdD8LoxVzGF/RPUKAcvmm49FQ0oxwDF3BGKtDXcEc+T1b2N+teh/OJfpU0jr6"
        crossorigin="anonymous"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/contrib/auto-render.min.js"
        integrity="sha384-hCXGrW6PitJEwbkoStFjeJxv+fSOOQKOPbJxSfM6G5sWZjAyWhXiTIIAmQqnlLlh" crossorigin="anonymous"
        onload="renderMathInElement(document.body);"></script>

    <link rel="stylesheet" href="style.css">
    '''
    head.append(BeautifulSoup(katex_tags, "html.parser"))

# 删除 document-subtitle div
for div in soup.find_all("div", class_="document-subtitle"):
    div.decompose()

# 删除内容为“目录”的h2所在的div
for h2 in soup.find_all("h2"):
    if h2.get_text(strip=True) == "目录":
        parent_div = h2.find_parent("div")
        if parent_div:
            parent_div.decompose()

# 删除所有 <hr> 标签
for hr in soup.find_all("hr"):
    hr.decompose()

# 删除部分样式属性
for tag in soup.find_all(style=True):
    styles = map(str.strip, tag['style'].split(';'))

    filtered_styles = []
    for style in filter(None, styles):
        name, value = map(str.strip, style.split(':', 1))
        include_names = ["color"]
        if name in include_names:
            filtered_styles.append(f"{name}: {value};")

    if filtered_styles:
        tag['style'] = ' '.join(filtered_styles)
    else:
        del tag['style']

# 将所有没有属性的<div>标签转换为<p>标签
for div in soup.find_all("div"):
    if not div.attrs:
        p_tag = soup.new_tag("p")
        p_tag.extend(div.contents)
        div.replace_with(p_tag)

# 将所有 <span class="equation"> 的文本用 \( 和 \) 包裹
for span in soup.find_all("span", class_="equation"):
    if span.string:
        # 使用strip()去除首尾空格
        equation_text = span.string.strip()
        # 用 \( 和 \) 包裹
        wrapped_text = f"\\({equation_text}\\)"
        # 替换span的内容
        span.string = wrapped_text


# 将处理后的内容写入新的HTML文件
with open("初步处理.html", "w", encoding="utf-8") as file:
    file.write(str(soup))
