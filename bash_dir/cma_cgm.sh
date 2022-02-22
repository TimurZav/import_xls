echo ${XL_IDP_ROOT}
xls_path="${XL_IDP_ROOT}/cma_cgm/"
echo $xls_path

# xls_path=/home/ruscon/Import_xls/НУТЭП\ -\ ноябрь/CMA-CGM/
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
    python3 ../scripts_for_bash/"cma_cgm.py" "${csv_name}" "${xls_path}"/json
        
    mv "${file}" "${done_path}"
    mv "${csv_name}" "${done_path}"
done