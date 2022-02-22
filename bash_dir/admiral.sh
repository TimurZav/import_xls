echo ${XL_IDP_ROOT}
xls_path="${XL_IDP_ROOT}/admiral/"
echo $xls_path
# xls_path=/home/ruscon/Import_xls/НУТЭП\ -\ ноябрь/ADMIRAL/
mkdir "${xls_path}"/csv
mkdir "${xls_path}"/json

done_path="${xls_path}"/done
mkdir "${done_path}"

for file in "${xls_path}"/*.xls*;
do
    echo "'${file}'";
    csv_name="${xls_path}/csv/$(basename "${file}").csv"
    echo "Will convert Excel '${file}' to CSV '${csv_name}'"
    in2csv "${file}" > "${csv_name}"
    python3 ../scripts_for_bash/admiral.py "${csv_name}" "${xls_path}"/json
    mv "${file}" "${done_path}"
    mv "${csv_name}" "${done_path}"
done

for file in "${xls_path}"/*.XLS*;
do
    echo "'${file}'";
    csv_name="${xls_path}/csv/$(basename "${file}").csv"
    echo "Will convert Excel '${file}' to CSV '${csv_name}'"
    in2csv "${file}" > "${csv_name}"
    python3 ../scripts_for_bash/admiral.py "${csv_name}" "${xls_path}"/json
    mv "${file}" "${done_path}"
    mv "${csv_name}" "${done_path}"
done

#xls_path=/home/timur/PycharmWork/PORT_LINE_CSV/test
#path="${xls_path}"/* | tr A-Z a-z
#echo "${path}"
#for file in "${xls_path}/"*.csv | tr A-Z a-z;
#do
#    echo "${file}"
#done


#files_count="$(ls -l $xls_list | wc -l)"
#echo "Will work on ${files_count} in folder ${xls_path}"
#for xls in ${xls_list}
#do
#  echo "${xls}"
##	csv_name="${xls_path}/csv/$(basename "$xls").csv"
##  	echo "Will convert Excel $xls to CSV ${csv_name}"
##  	in2csv "$xls" > "$csv_name"
##  	mv "$xls" "${xls_path}/excel_pushed_to_csv"
##
##  	/bin/sh "${xls_path}/csv2json.sh" "$csv_name"
#done