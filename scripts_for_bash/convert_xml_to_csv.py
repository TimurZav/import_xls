import csv
import sys
import xml.etree.cElementTree as ET

directory = sys.argv[1]
path_to_right_csv = sys.argv[2]
ns = {"doc": "urn:schemas-microsoft-com:office:spreadsheet", "ss": "urn:schemas-microsoft-com:office:spreadsheet"}
tree = ET.parse(directory)
root = tree.getroot()


def getvalueofnode(node):
    """ return node text or None """
    return node.text if node is not None else None


def main():
    data = list()
    for i, node in enumerate(root.findall(".//doc:Row", ns)):
        if i > 3:
            data.append({'id': getvalueofnode(node.find('doc:Cell[1]/doc:Data', ns)),
                         'number_container': getvalueofnode(node.find('doc:Cell[2]/doc:Data', ns)),
                         'size_container': getvalueofnode(node.find('doc:Cell[3]/doc:Data', ns)),
                         'type_container': getvalueofnode(node.find('doc:Cell[4]/doc:Data', ns)),
                         'tara': getvalueofnode(node.find('doc:Cell[5]/doc:Data', ns)),
                         'plomb': getvalueofnode(node.find('doc:Cell[6]/doc:Data', ns)),
                         'black_mode':getvalueofnode(node.find('doc:Cell[7]/doc:Data', ns)),
                         'goods_name': getvalueofnode(node.find('doc:Cell[8]/doc:Data', ns)),
                         'count_places': getvalueofnode(node.find('doc:Cell[9]/doc:Data', ns)),
                         'address': getvalueofnode(node.find('doc:Cell[10]/doc:Data', ns)),
                         'weight': getvalueofnode(node.find('doc:Cell[11]/doc:Data', ns)),
                         'bill': getvalueofnode(node.find('doc:Cell[12]/doc:Data', ns)),
                         'shipper': getvalueofnode(node.find('doc:Cell[13]/doc:Data', ns)),
                         'country': getvalueofnode(node.find('doc:Cell[14]/doc:Data', ns)),
                         'country_getting': getvalueofnode(node.find('doc:Cell[15]/doc:Data', ns)),
                         'company_getting': getvalueofnode(node.find('doc:Cell[16]/doc:Data', ns)),
                         'shipper_getting': getvalueofnode(node.find('doc:Cell[17]/doc:Data', ns)),
                        })
    return data


my_dict = main()

with open(path_to_right_csv + ".csv", 'w') as f:
    for i, key in enumerate(my_dict):
        w = csv.DictWriter(f, my_dict[i].keys())
        w.writerow(my_dict[i])
