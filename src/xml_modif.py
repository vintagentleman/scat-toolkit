from xml.dom import minidom
from xml.dom.minidom import Node


class PostProc:
    @classmethod
    def remove_blanks(cls, node):
        for x in node.childNodes:
            if x.nodeType == Node.TEXT_NODE:
                if x.nodeValue:
                    x.nodeValue = x.nodeValue.strip()
            elif x.nodeType == Node.ELEMENT_NODE:
                cls.remove_blanks(x)

    def __init__(self, fo):
        self.xml = minidom.parse(fo)
        self.remove_blanks(self.xml)
        self.xml.normalize()

        self.nums = self.xml.getElementsByTagName("num")
        self.names = self.xml.getElementsByTagName("name")

    def modif_num(self):
        def pack_num(node):
            next_node = node.nextSibling

            if (
                next_node is not None
                and next_node.tagName == "pc"
                and next_node.getAttribute("force") != "strong"
            ):
                next_node.tagName = "c"
                next_node.removeAttribute("force")
                node.appendChild(next_node)
                pack_num(node)
            elif next_node is not None and next_node.tagName == "num":
                node.appendChild(next_node.firstChild)
                node.parentNode.removeChild(next_node)
                self.nums.remove(next_node)
                pack_num(node)

        for num in self.nums:
            # Упаковка <pc> в препозиции
            prev_node = num.previousSibling
            if (
                prev_node.tagName == "pc"
                and prev_node.getAttribute("force") != "strong"
            ):
                prev_node.tagName = "c"
                prev_node.removeAttribute("force")
                num.insertBefore(prev_node, num.firstChild)
            # Последовательная упаковка <pc> и <num> в постпозиции
            pack_num(num)

            # Суммирование числовых значений
            total = sum(
                [
                    int(node.getAttribute("reg"))
                    for node in num.getElementsByTagName("w")
                ]
            )
            num.setAttribute("value", str(total))

    def modif_name(self):
        def pack_name(node):
            next_node = node.nextSibling

            if next_node is not None and next_node.tagName == "name":
                node.appendChild(next_node.firstChild)
                node.parentNode.removeChild(next_node)
                self.names.remove(next_node)
                pack_name(node)

        for name in self.names:
            pack_name(name)

    def run(self):
        self.modif_num()
        self.modif_name()

        return self.xml
