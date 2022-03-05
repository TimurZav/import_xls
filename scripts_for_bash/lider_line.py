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


def add_data_to_parced(parsed_data, line, context, num1, num2, num3, num4, num5, num6, num7, num8):
    range_id = line[:2]
    match_id = [isDigit(id) for id in range_id]
    add_id = match_id.index(True)
    line_id = str(float(range_id[add_id]))
    if isDigit(line_id):
        logging.info(u"Ok, line looks common...")
        date = datetime.datetime.strptime(line[add_id + num4], "%d.%m.%Y")
        parsed_record = {
            'container_number': line[add_id + 1].strip(),
            'container_size': int(float(line[add_id + 2])),
            'container_type': line[add_id + 3].strip(),
            'goods_name_rus': line[add_id + 7].strip(),
            'package_number': int(float(line[add_id + num1])),
            'goods_weight': float(line[add_id + num2]) if line[add_id + num2] else None,
            'consignment': line[add_id + num3].strip(),
            'date': str(date.date()),
            'shipper': line[add_id + num5].strip(),
            'shipper_country': line[add_id + num6].strip(),
            'consignee': line[add_id + num7].strip(),
            'city': line[add_id + num8].strip()
        }

        record = merge_two_dicts(context, parsed_record)
        logging.info(u"record is {}".format(record))
        parsed_data.append(record)
        return parsed_record


class OoclCsv(object):

    def __init__(self):
        pass

    def process(self, input_file_path):
        context = dict(line=os.path.basename(__file__).replace(".py", ""))
        context['terminal'] = os.environ.get('XL_IMPORT_TERMINAL')
        context['parsed_on'] = str(datetime.datetime.now().date())
        parsed_data = list()

        goods_name_eng = None

        with open(input_file_path, newline='') as csvfile:
            lines = list(csv.reader(csvfile))

        logging.info(u'lines type is {} and contain {} items'.format(type(lines), len(lines)))
        logging.info(u'First 3 items are: {}'.format(lines[:3]))

        for ir, line in enumerate(lines):
            logging.info(u'line {} is {}'.format(ir, line))
            str_list = list(filter(bool, line))
            if ir == 3:
                logging.info(u"Will parse ship and trip in value '{}'...".format(line[2], line[6]))
                split_on = u'рейс:'
                logging.info(u"substring to split on is '{}'".format(split_on))
                context['ship'] = line[2].strip()
                context['voyage'] = line[6].strip()
                logging.info(u"context now is {}".format(context))
                continue
            if ir == 5:
                context['voyage'] = line[2].strip()
                logging.info(u"context now is {}".format(context))
                continue
            if ir == 7:
                logging.info("Will parse date in value {}...".format(line[2]))
                context['date'] = line[2] if line[2] else "1970-01-01"
                logging.info(u"context now is {}".format(context))
                continue
            if ir > 8 and bool(str_list):
                try:
                    if re.match("английское", line[8]):
                        goods_name_eng = line[8].strip()
                    add_data_to_parced(parsed_data, line, context, 9, 10, 11, 12, 13, 14, 15, 16)
                except:
                    if goods_name_eng is None:
                        try:
                            add_data_to_parced(parsed_data, line, context, 8, 9, 10, 11, 12, 13, 14, 15)
                        except:
                            continue
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