import csv
import os
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

        for ir, line in enumerate(lines):
            logging.info(u'line {} is {}'.format(ir, line))
            str_list = list(filter(bool, line))
            if ir == 2:
                logging.info(u"Will parse ship and trip in value '{}'...".format(line[2], line[6]))
                context['ship'] = line[2].strip()
                context['voyage'] = line[6].strip()
                logging.info(u"context now is {}".format(context))
                continue
            if ir == 6:
                logging.info("Will parse date in value {}...".format(line[2]))
                context['date'] = line[2]
                logging.info(u"context now is {}".format(context))
                continue
            if ir > 8 and bool(str_list):  # Была на 11 итерация
                try:
                    logging.info(u"Checking if we are on common line with number...")
                    range_id = line[0:2]
                    match_id = [isDigit(id) for id in range_id]
                    add_id = match_id.index(True)
                    line_id = str(float(range_id[add_id]))
                    if isDigit(line_id):
                        logging.info(u"Ok, line looks common...")
                        parsed_record = dict()
                        parsed_record['container_number'] = line[add_id + 1]
                        parsed_record['container_size'] = int(float(line[add_id + 2]))
                        parsed_record['container_type'] = line[add_id + 3]
                        parsed_record['goods_weight'] = float(line[add_id + 8])
                        parsed_record['package_number'] = int(float(line[add_id + 5]))
                        parsed_record['goods_name_rus'] = line[add_id + 6]
                        parsed_record['consignment'] = line[add_id + 10]
                        parsed_record['shipper'] = line[add_id + 12]
                        parsed_record['shipper_country'] = line[add_id + 13]
                        parsed_record['consignee'] = line[add_id + 14]
                        city = [i for i in line[add_id + 14].split(', ')][1:]
                        parsed_record['city'] = " ".join(city)
                        record = merge_two_dicts(context, parsed_record)
                        logging.info(u"record is {}".format(record))
                        parsed_data.append(record)
                except:
                    continue

        logging.error(u"About to write parsed_data to output: {}".format(parsed_data))
        return parsed_data

# dir_name = 'НУТЭП - ноябрь/Economou/csv/'
# input_file_path = 'Копия уведомление о прибытии JONATHAN P 2144N  - HL.xls.csv'
input_file_path = os.path.abspath(sys.argv[1])
output_folder = sys.argv[2]
basename = os.path.basename(input_file_path)
output_file_path = os.path.join(output_folder, basename+'.json')
print("output_file_path is {}".format(output_file_path))


parsed_data = OoclCsv().process(input_file_path)

with open(output_file_path, 'w', encoding='utf-8') as f:
    json.dump(parsed_data, f, ensure_ascii=False, indent=4)