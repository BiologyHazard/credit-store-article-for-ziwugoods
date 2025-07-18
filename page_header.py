from bs4 import BeautifulSoup, ResultSet, Tag
from bs4.element import PageElement
import copy

def copy_and_remove_sup(tag: Tag | None) -> Tag | None:
    """
    复制标签并移除其中的<sup>标签

    Args:
        tag: 要处理的BeautifulSoup标签对象，可以为None

    Returns:
        Tag | None: 处理后的标签副本，如果输入为None则返回None
    """
    if tag is None:
        return None
    # 深拷贝标签避免修改原始标签
    tag = copy.deepcopy(tag)
    # 查找并移除所有<sup>标签
    for sup in tag.find_all("sup"):
        sup.decompose()
    return tag



def main():
    """
    主函数：处理HTML文件的页眉信息
    读取index.html文件，为页眉添加页码和标题信息
    """
    # 读取HTML文件
    with open("index.html", "r", encoding="utf-8") as fp:
        soup = BeautifulSoup(fp, "html.parser")

    # 用于存储标题ID到编号的映射
    id_to_numbering = {}
    # 各级标题的计数器
    h1_counter = 0
    h2_counter = 0
    h3_counter = 0

    # 遍历所有带有auto-numbering类的标题标签，生成编号
    for tag in soup.find_all(["h1", "h2", "h3"], class_="auto-numbering"):
        if tag.name == "h1":
            h1_counter += 1
            h2_counter = 0  # 重置二级标题计数器
            h3_counter = 0  # 重置三级标题计数器
            id_to_numbering[tag["id"]] = f"{h1_counter}"
        elif tag.name == "h2":
            h2_counter += 1
            h3_counter = 0  # 重置三级标题计数器
            id_to_numbering[tag["id"]] = f"{h1_counter}.{h2_counter}"
        elif tag.name == "h3":
            h3_counter += 1
            id_to_numbering[tag["id"]] = f"{h1_counter}.{h2_counter}.{h3_counter}"

    # 存储每个页眉对应的标题信息
    belong_h1_list: list[Tag | None] = []        # 存储对应的h1标题
    belong_h1_or_h2_list: list[Tag | None] = []  # 存储对应的h1或h2标题

    # 遍历所有页眉div（跳过第一个）
    for page_header_div in soup.find_all("div", class_="page-header")[1:]:
        # 查找页眉前最近的h1标题
        previous_h1 = page_header_div.find_previous("h1", class_="auto-numbering")
        # 查找页眉前最近的h1或h2标题
        previous_h1_or_h2 = page_header_div.find_previous(["h1", "h2"], class_="auto-numbering")
        # 复制标题并移除sup标签后添加到列表
        belong_h1_list.append(copy_and_remove_sup(previous_h1))
        belong_h1_or_h2_list.append(copy_and_remove_sup(previous_h1_or_h2))

    # 为最后一页添加对应的标题信息
    last_h1 = soup.find_all("h1", class_="auto-numbering")[-1]
    last_h1_or_h2 = soup.find_all(["h1", "h2"], class_="auto-numbering")[-1]
    belong_h1_list.append(copy_and_remove_sup(last_h1))
    belong_h1_or_h2_list.append(copy_and_remove_sup(last_h1_or_h2))

    # 打印ID到编号的映射（用于调试）
    print(id_to_numbering)

    # 遍历所有页眉div，生成页眉内容
    for i, (page_header_div, belong_h1, belong_h1_or_h2) in enumerate(zip(
        soup.find_all("div", class_="page-header"),
        belong_h1_list,
        belong_h1_or_h2_list,
    )):
        page_num = i + 1  # 页码从1开始

        # 处理页码div：如果存在则清空并移除，否则创建新的
        if (page_num_div := page_header_div.find("div", class_="page-number")) is not None:
            page_num_div.clear()
            page_num_div.extract()
        else:
            page_num_div = soup.new_tag("div", attrs={"class": ["page-number"]})

        # 处理页面信息div：如果存在则清空并移除，否则创建新的
        if (page_info_div := page_header_div.find("div", class_="page-info")) is not None:
            page_info_div.clear()
            page_info_div.extract()
        else:
            page_info_div = soup.new_tag("div", attrs={"class": ["page-info"]})

        # 创建页码span标签
        page_num_span = soup.new_tag("span", lang="en", string=str(page_num))
        page_num_div.append(page_num_span)

        # 根据页码奇偶性选择不同的标题
        if page_num % 2 == 0:
            tag = belong_h1      # 偶数页使用h1标题
        else:
            tag = belong_h1_or_h2  # 奇数页使用h1或h2标题

        # 检查页眉后是否紧跟h1标题，如果是则跳过处理
        if page_header_div.next_sibling.next_sibling.name == "h1":
            print(f"{page_num}页的页眉没有对应的标题，跳过")
        else:
            # 如果有对应的标题，则添加编号和标题内容
            if tag is not None:
                numbering = id_to_numbering[tag["id"]]
                numbering_span = soup.new_tag("span", lang="en", string=numbering)
                space_span = soup.new_tag("span", lang="zh", string="　")  # 全角空格
                contents = [numbering_span, space_span, *tag.contents]
                page_info_div.extend(contents)

        # 清空页眉div并重新添加内容
        page_header_div.clear()

        # 根据页码奇偶性调整页码和页面信息的位置
        if page_num % 2 == 0:
            # 偶数页：页码在左，页面信息在右
            page_header_div.append(page_num_div)
            page_header_div.append(page_info_div)
        else:
            # 奇数页：页面信息在左，页码在右
            page_header_div.append(page_info_div)
            page_header_div.append(page_num_div)

    # 编号到页码的映射
    numbering_to_page_num = {}
    page_header_div_list: ResultSet[PageElement] = soup.find_all("div", class_="page-header")
    for tag in soup.find_all(["h1", "h2", "h3"], class_="auto-numbering"):
        previous_page_header_div = tag.find_previous("div", class_="page-header")
        assert previous_page_header_div is not None, "没有找到对应的页眉div"
        # 获取页码
        page_num = page_header_div_list.index(previous_page_header_div) + 1
        # 将编号和页码存入字典
        numbering_to_page_num[id_to_numbering[tag["id"]]] = page_num

    print(numbering_to_page_num)

    # 获取目录的层级格式
    for h1_counter, h1_li in enumerate(soup.find("div", class_="catalog").ol.find_all("li", recursive=False), start=1):
        numbering = f"{h1_counter}"
        page_num = numbering_to_page_num[numbering]
        print(f"{h1_counter}. {h1_li.find("span", class_="title-text").string} (Page {page_num})")
        h1_li.find("span", class_="catalog-page-number").string = str(page_num)
        if h1_li.ol is not None:
            for h2_counter, h2_li in enumerate(h1_li.ol.find_all("li", recursive=False), start=1):
                numbering = f"{h1_counter}.{h2_counter}"
                page_num = numbering_to_page_num[numbering]
                print(f"  {h1_counter}.{h2_counter}. {h2_li.find('span', class_='title-text').string} (Page {page_num})")
                h2_li.find("span", class_="catalog-page-number").string = str(page_num)
                if h2_li.ol is not None:
                    for h3_counter, h3_li in enumerate(h2_li.ol.find_all("li", recursive=False), start=1):
                        numbering = f"{h1_counter}.{h2_counter}.{h3_counter}"
                        page_num = numbering_to_page_num[numbering]
                        print(f"    {h1_counter}.{h2_counter}.{h3_counter}. {h3_li.find('span', class_='title-text').string} (Page {page_num})")
                        h3_li.find("span", class_="catalog-page-number").string = str(page_num)



    # 将修改后的HTML写回文件
    with open("index.html", "w", encoding="utf-8") as fp:
        fp.write(str(soup))


if __name__ == "__main__":
    main()
