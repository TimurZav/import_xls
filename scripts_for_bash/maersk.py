import csv
import os
import re
import logging
import sys
import json

if not os.path.exists("logging"):
    os.mkdir("logging")

logging.basicConfig(filename="logging/{}.log".format(os.path.basename(__file__)), level=logging.DEBUG)
log = logging.getLogger()


def merge_two_dicts(x, y):
    z = x.copy()   # start with keys and values of x
    z.update(y)    # modifies z with keys and values of y
    return z


def isDigit(x):
    try:
        float(x)
        return True
    except ValueError:
        return False


class OoclCsv(object):

    def __init__(self):
        pass

    def process(self, input_file_path):
        context = dict(line=os.path.basename(__file__).replace(".py", ""))
        context['terminal'] = "НУТЭП"
        parsed_data = list()

        with open(input_file_path, newline='') as csvfile:
            lines = list(csv.reader(csvfile))

        logging.info(u'lines type is {} and contain {} items'.format(type(lines), len(lines)))
        logging.info(u'First 3 items are: {}'.format(lines[:3]))
        parsed_record = dict()
        for ir, line in enumerate(lines):
            logging.info(u'line {} is {}'.format(ir, line))
            str_list = list(filter(bool, line))
            true_line = bool(line[0]), bool(line[1]), bool(line[2]), bool(line[3]), bool(line[5]), bool(line[8])
            if ir == 1:
                logging.info(u"Will parse ship and trip in value '{}'...".format(line[1], line[3]))
                context['ship'] = line[1]
                context['voyage'] = line[3]
                logging.info(u"context now is {}".format(context))
                continue
            if ir > 1 and bool(str_list):
                try:
                    if true_line == (True, False, False, False, True, False):
                        logging.info(u"Checking if we are on common line with number...")
                        context['date'] = line[0].rsplit(' ')[0]
                    elif true_line == (True, True, True, False, True, False):
                        logging.info(u"Ok, line looks common...")
                        parsed_record['shipper'] = line[1]
                        city = [i for i in line[2].split(', ')][1:]
                        parsed_record['city'] = " ".join(city)
                    elif true_line == (False, False, True, True, True, False) or true_line == (False, False, False, True,
                                                                                        True, False):
                        parsed_record['consignee'] = line[2]
                        parsed_record['container_number'] = line[3]
                        container_size_and_type = re.findall("\w{2}", line[5])
                        parsed_record['container_size'] = int(float(container_size_and_type[0]))
                        parsed_record['container_type'] = container_size_and_type[1]
                        parsed_record['goods_weight'] = float(line[10])
                        parsed_record['package_number'] = line[11]

                        record = merge_two_dicts(context, parsed_record)
                        logging.info(u"record is {}".format(record))
                        parsed_data.append(record)
                    elif true_line == (True, False, False, False, False, False):
                        context['goods_name_rus'] = line[0]

                        record = merge_two_dicts(context, parsed_record)
                        logging.info(u"record is {}".format(record))
                        parsed_data.append(record)
                    if bool(re.findall('(^\d{9}$|^[a-zA-Z]{3}\d{6}$|^[a-zA-Z]{6}\d{3}$|\d{2}[a-zA-Z]\d{6}|^[a-zA-Z]{'
                                       '1}[0-9a-zA-Z]{6}[_]\d{3}|\d{1}[a-zA-Z]{2}\d{6}|[0-9a-zA-Z]{7}[_]\d{3}|\d{1}['
                                       '0-9a-zA-Z]{8})', line[0])):
                        context['goods_name_rus'] = ''
                except:
                    continue

        logging.error(u"About to write parsed_data to output: {}".format(parsed_data))
        return parsed_data


# dir_name = "/home/timur/PycharmWork/PORT_LINE_CSV/НУТЭП - ноябрь/MAERSK - собирает робот/csv/"
# input_file_path = "man-T9X143W-All.xls.csv"
input_file_path = os.path.abspath(sys.argv[1])
output_folder = sys.argv[2]
basename = os.path.basename(input_file_path)
output_file_path = os.path.join(output_folder, basename+'.json')
print("output_file_path is {}".format(output_file_path))


parsed_data = OoclCsv().process(input_file_path)

with open(output_file_path, 'w', encoding='utf-8') as f:
    json.dump(parsed_data, f, ensure_ascii=False, indent=4)
