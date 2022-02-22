echo ${XL_IDP_ROOT}
xls_path="${XL_IDP_ROOT}/lider_line/"
echo $xls_path

# xls_path=/home/ruscon/Import_xls/НУТЭП\ -\ ноябрь/LIDER\ LINE/
mkdir "${xls_path}"/from_xml_to_csv
mkdir "${xls_path}"/json

done_path="${xls_path}"/done
mkdir "${done_path}"

for file in "${xls_path}"/*.xml;
do
    python3 ../scripts_for_bash/"convert_xml_to_csv.py" "${file}" "${xls_path}/from_xml_to_csv/$(basename "${file}")"
    csv_name="${xls_path}/from_xml_to_csv/$(basename "${file}").csv"
    python3 ../scripts_for_bash/"from_raw_csv_to_right_csv.py" "${csv_name}" "${xls_path}"/json
        
    mv "${file}" "${done_path}"
    mv "${csv_name}" "${done_path}"
done