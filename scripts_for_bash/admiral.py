import csv
import datetime
import os
import logging
import re
import sys
import json

month_list = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября",
         "декабря"]
month_list_upper = [month.upper() for month in month_list]
month_list_title = [month.title() for month in month_list]
# month_list = month_list_upper + month_list + month_list_title

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


def add_value_to_dict(parsed_record, goods_weight, package_number, name_rus, consignment, city, shipper,
                      shipper_country, consignee,
                      context):
    parsed_record['goods_weight'] = float(goods_weight)
    parsed_record['package_number'] = int(float(package_number))
    parsed_record['goods_name_rus'] = name_rus
    parsed_record['consignment'] = consignment
    parsed_record['city'] = city
    parsed_record['shipper'] = shipper
    parsed_record['shipper_country'] = shipper_country
    parsed_record['consignee'] = consignee
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
        var_name_ship = "ВЫГРУЗКА ГРУЗА С Т/Х "
        with open(input_file_path, newline='') as csvfile:
            lines = list(csv.reader(csvfile))

        logging.info(u'lines type is {} and contain {} items'.format(type(lines), len(lines)))
        logging.info(u'First 3 items are: {}'.format(lines[:3]))
        for ir, line in enumerate(lines):
            logging.info(u'line {} is {}'.format(ir, line))
            str_list = list(filter(bool, line))
            if ir == 4:
                logging.info(u"Will parse ship and trip in value '{}'...".format(line[1]))
                split_on = u'рейс:'
                logging.info(u"substring to split on is '{}'".format(split_on))
                ship_and_voyage_str = line[1].replace(var_name_ship, "")
                ship_and_voyage_list = ship_and_voyage_str.rsplit(' ', 1)
                context['ship'] = ship_and_voyage_list[0]
                context['voyage'] = re.sub(r'[^\w\s]', '', ship_and_voyage_list[1])
                logging.info(u"context now is {}".format(context))
                continue
            if ir == 6:
                try:
                    logging.info("Will parse date in value {}...".format(line[1].rsplit(': ', 1)[1]))
                    month = line[1].rsplit(':  ', 1)[1].rsplit(' ', 3)
                    if month[1] in month_list:
                        month_digit = month_list.index(month[1]) + 1
                    date = datetime.datetime.strptime(month[2] + '-' + str(month_digit) + '-' + month[0], "%Y-%m-%d")
                    context['date'] = str(date.date())
                    logging.info(u"context now is {}".format(context))
                    continue
                except:
                    context['date'] = "1970-01-01"
                    continue
            if ir > 11 and bool(str_list):
                try:
                    logging.info(u"Checking if we are on common line with number...")
                    parsed_record = dict()
                    if isDigit(line[1]) or (not line[0] and not line[1] and not line[2] and not line[3]):
                        try:
                            container_size_and_type = re.findall("\w{2}", line[2])
                            parsed_record['container_size'] = int(float(container_size_and_type[0]))
                            parsed_record['container_type'] = container_size_and_type[1]
                            parsed_record['container_number'] = line[3]
                            last_container_number.append(line[3])
                            last_container_size.append(container_size_and_type[0])
                            last_container_type.append(container_size_and_type[1])
                            record = add_value_to_dict(parsed_record, line[7], line[8], line[9], line[13], line[14],
                                                       line[10], line[11],
                                                       line[12],
                                                       context)
                            logging.info(u"record is {}".format(record))
                            parsed_data.append(record)
                        except IndexError:
                            parsed_record['container_size'] = last_container_size[-1]
                            parsed_record['container_type'] = last_container_type[-1]
                            parsed_record['container_number'] = last_container_number[-1]
                            record = add_value_to_dict(parsed_record, line[7], line[8], line[9], line[13], line[14],
                                                       line[10], line[11],
                                                       line[12], context)
                            logging.info(u"record is {}".format(record))
                            parsed_data.append(record)
                except Exception as ex:
                    continue

        logging.error(u"About to write parsed_data to output: {}".format(parsed_data))
        return parsed_data


# dir_name = "/home/timur/PycharmWork/PORT_LINE_CSV/НУТЭП - ноябрь/ADMIRAL/csv/"
# input_file_path = "ADMIRAL SUN от 11.11.21.XLS.csv"
input_file_path = os.path.abspath(sys.argv[1])
output_folder = sys.argv[2]
basename = os.path.basename(input_file_path)
output_file_path = os.path.join(output_folder, basename+'.json')
print("output_file_path is {}".format(output_file_path))


parsed_data = OoclCsv().process(input_file_path)

with open(output_file_path, 'w', encoding='utf-8') as f:
    json.dump(parsed_data, f, ensure_ascii=False, indent=4)

