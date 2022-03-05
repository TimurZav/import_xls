import csv
import datetime
import os
import logging
import re
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


def add_value_to_dict(parsed_record, goods_weight, package_number, name_rus, consignment, shipper, shipper_country,
                      consignee,
                      city, context):
    parsed_record['goods_weight'] = float(goods_weight)
    parsed_record['package_number'] = int(float(package_number))
    parsed_record['goods_name_rus'] = name_rus
    parsed_record['consignment'] = consignment
    parsed_record['shipper'] = shipper
    parsed_record['shipper_country'] = shipper_country
    parsed_record['consignee'] = consignee
    parsed_record['city'] = " ".join(city).strip()
    return merge_two_dicts(context, parsed_record)


class OoclCsv(object):

    def __init__(self):
        pass

    def process(self, input_file_path):
        context = dict(line=os.path.basename(__file__).replace(".py", ""))
        context['terminal'] = os.environ.get('XL_IMPORT_TERMINAL')
        context['parsed_on'] = str(datetime.datetime.now().date())
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
            if ir == 5:
                logging.info(u"Will parse ship and trip in value '{}'...".format(line[2]))
                split_on = u'рейс:'
                logging.info(u"substring to split on is '{}'".format(split_on))
                context['ship'] = line[2].rsplit('  ', 1)[0]
                voyage = line[2].rsplit('  ', 1)[1]
                context['voyage'] = voyage.rsplit(': ', 1)[1]
                logging.info(u"context now is {}".format(context))
                continue
            if ir == 7:
                try:
                    logging.info("Will parse date in value {}...".format(line[2]))
                    date = datetime.datetime.strptime(line[2], "%d.%m.%Y")
                    context['date'] = str(date.date())
                    logging.info(u"context now is {}".format(context))
                    continue
                except IndexError:
                    context['date'] = ""
                    logging.info("There's not a month in file")
                    continue
            if ir > 12 and bool(str_list):
                try:
                    logging.info(u"Checking if we are on common line with number...")
                    # range_id = line[0:2]
                    # match_id = [isDigit(id) for id in range_id]
                    # add_id = match_id.index(True)
                    # line_id = str(float(range_id[add_id]))
                    logging.info(u"Ok, line looks common...")
                    parsed_record = dict()
                    if isDigit(line[0]):
                        parsed_record['container_number'] = line[1].strip()
                        parsed_record['container_size'] = int(float(line[2]))
                        parsed_record['container_type'] = line[3].strip()
                        last_container_number.append(line[1].strip())
                        last_container_size.append(line[2].strip())
                        last_container_type.append(line[3].strip())
                        city = [i for i in line[12].split(', ')][1:]
                        record = add_value_to_dict(parsed_record, line[8], line[5], line[6].strip(), line[9].strip(),
                                                   line[10].strip(),
                                                   line[11].strip(),
                                                   line[12].strip(), city, context)
                        logging.info(u"record is {}".format(record))
                        parsed_data.append(record)
                    elif not line[0] and not line[1] and not line[2] and not line[3]:
                        parsed_record['container_size'] = int(float(last_container_size[-1]))
                        parsed_record['container_type'] = last_container_type[-1]
                        parsed_record['container_number'] = last_container_number[-1]
                        city = [i for i in line[12].split(', ')][1:]
                        record = add_value_to_dict(parsed_record, line[8], line[5], line[6].strip(), line[9].strip(),
                                                   line[10].strip(),
                                                   line[11].strip(),
                                                   line[12].strip(), city, context)
                        logging.info(u"record is {}".format(record))
                        parsed_data.append(record)
                except Exception as ex:
                    continue

        logging.error(u"About to write parsed_data to output: {}".format(parsed_data))
        return parsed_data


# dir_name = "/home/timur/PycharmWork/PORT_LINE_CSV/НУТЭП - ноябрь/OOCL/csv/"
# input_file_path = "Копия Уведомление о прибытии AS FATIMA 138N.xls.csv"
input_file_path = os.path.abspath(sys.argv[1])
output_folder = sys.argv[2]
basename = os.path.basename(input_file_path)
output_file_path = os.path.join(output_folder, basename+'.json')
print("output_file_path is {}".format(output_file_path))


parsed_data = OoclCsv().process(input_file_path)

with open(output_file_path, 'w', encoding='utf-8') as f:
    json.dump(parsed_data, f, ensure_ascii=False, indent=4)
