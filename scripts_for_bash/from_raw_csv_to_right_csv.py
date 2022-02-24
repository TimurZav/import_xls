import csv
import datetime
import os
import logging
import sys
import json

if not os.path.exists("logging"):
    os.mkdir("logging")

logging.basicConfig(filename="logging/{}.log".format(os.path.basename(__file__)), level=logging.DEBUG)
log = logging.getLogger()


def merge_two_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z


def isDigit(x):
    try:
        float(x)
        return True
    except ValueError:
        return False


def add_value_to_dict(parsed_record, goods_weight, package_number, name_rus, consignment, date, shipper,
                      shipper_country, consignee, city, context):
    parsed_record['goods_weight'] = float(goods_weight)
    parsed_record['package_number'] = int(float(package_number))
    parsed_record['goods_name_rus'] = name_rus
    parsed_record['consignment'] = consignment
    date = datetime.datetime.strptime(date, "%d.%m.%Y")
    parsed_record['date'] = str(date.date())
    parsed_record['shipper'] = shipper
    parsed_record['shipper_country'] = shipper_country
    parsed_record['consignee'] = consignee
    parsed_record['city'] = city
    return merge_two_dicts(context, parsed_record)


class OoclCsv(object):

    def __init__(self):
        pass

    def process(self, input_file_path):
        context = dict(line="lider_line")
        context["терминал"] = "НУТЭП"
        parsed_data = list()
        last_container_number = list()
        last_container_size = list()
        last_container_type = list()
        with open(input_file_path, newline='') as csvfile:
            lines = list(csv.reader(csvfile))

        logging.info(u'lines type is {} and contain {} items'.format(type(lines), len(lines)))
        logging.info(u'First 3 items are: {}'.format(lines[:3]))
        for ir, line in enumerate(lines):
            logging.info(u'line {} is {}'.format(ir, line))
            str_list = list(filter(bool, line))
            if ir == 1:
                logging.info(u"Will parse trip in value '{}'...".format(line[2]))
                context['voyage'] = line[2]
                logging.info(u"context now is {}".format(context))
                continue
            if ir == 2:
                logging.info(u"Will parse ship in value '{}'...".format(line[2]))
                context['ship'] = line[2]
                logging.info(u"context now is {}".format(context))
                continue
            if ir == 3:
                logging.info("Will parse date in value {}...".format(line[2]))
                context['date'] = line[2]
                logging.info(u"context now is {}".format(context))
                continue
            if ir > 8 and bool(str_list):
                try:
                    logging.info(u"Checking if we are on common line with number...")
                    logging.info(u"Ok, line looks common...")
                    parsed_record = dict()
                    if isDigit(line[0]):
                        parsed_record['container_number'] = line[1]
                        parsed_record['container_size'] = int(float(line[2]))
                        parsed_record['container_type'] = line[3]
                        last_container_number.append(line[1])
                        last_container_size.append(line[2])
                        last_container_type.append(line[3])
                        record = add_value_to_dict(parsed_record, line[10], line[9], line[7], line[11], line[12], line[13],
                                                   line[14], line[15], line[16], context)
                        logging.info(u"record is {}".format(record))
                        parsed_data.append(record)
                    elif not line[0] and not line[1] and not line[2] and not line[3]:
                        parsed_record['container_size'] = int(float(last_container_size[-1]))
                        parsed_record['container_type'] = last_container_type[-1]
                        parsed_record['container_number'] = last_container_number[-1]
                        record = add_value_to_dict(parsed_record, line[10], line[9], line[7], line[11], line[12], line[13],
                                                   line[14], line[15], line[16], context)
                        logging.info(u"record is {}".format(record))
                        parsed_data.append(record)
                except Exception as ex:
                    continue

        logging.error(u"About to write parsed_data to output: {}".format(parsed_data))
        return parsed_data


input_file_path = os.path.abspath(sys.argv[1])
output_folder = sys.argv[2]
basename = os.path.basename(input_file_path)
output_file_path = os.path.join(output_folder, basename+'.json')
print("output_file_path is {}".format(output_file_path))

parsed_data = OoclCsv().process(input_file_path)

with open(output_file_path, 'w', encoding='utf-8') as f:
    json.dump(parsed_data, f, ensure_ascii=False, indent=4)
