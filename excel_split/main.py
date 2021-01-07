# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import sys
import os
import re
import xlwings as xw
from xlwings import constants

def get_files_by_dir(path):
    src_tmp = os.path.abspath(path).replace("\\", "/")
    src_filelist = []
    g = os.walk(src_tmp)
    for root, dirs, files in g:
        path = os.path.abspath(root).replace("\\", "/")
        for filename in files:
            if re.match('.*\.(xls|xlsx)', filename) and not re.match('new.*\.(xls|xlsx)', filename):
                p = os.path.join(path, filename).replace("\\", "/")
                src_filelist.append(p)
    if src_filelist:
        return src_filelist
    else:
        return None

def file_process(file_path_name, sheet_name, rows_start, rows_split_len):

    app = xw.App(visible=False, add_book=False)
    app.display_alerts = False
    app.screen_updating = False
    # 文件位置：filepath，打开test文档，然后保存，关闭，结束程序
    wb = app.books.open(file_path_name)
    try:
        sht = wb.sheets[sheet_name]
        nrow = sht.api.UsedRange.Rows.count


        rng = "A" + rows_start + ":B" + str(nrow)
        dcells = sht.range(rng).value


        wb.close()
        filepath, filename = os.path.split(file_path_name)
        new_file = filepath+'/new_'+filename

        if os.path.exists(new_file):
            os.remove(new_file)
        wb_n = app.books.add()
        sht_n = wb_n.sheets['sheet1']
        cc = 0
        r = 0
        c = 0
        n = int(rows_split_len)
        for dcell in dcells:
            print(dcell)
            if dcell[0]== None and dcell[1] == None:
                continue
            if r == 0:
                sht_n[r, c].value = "DEG"
                sht_n[r, c + 1].value = "LIFT"
                sht_n.range((r+1, c+1), (r+1, c+2)).api.HorizontalAlignment = constants.HAlign.xlHAlignRight
                sht_n.range((r+1, c+1), (r+1, c+2)).api.Font.Bold = True
                r += 1
            sht_n[r, c].value = dcell[0]
            sht_n[r, c+1].value = dcell[1]
            sht_n.range((r+1, c+1), (r+1, c+2)).api.HorizontalAlignment = constants.HAlign.xlHAlignRight
            r += 1
            cc += 1
            if cc == n:
                c += 2
                r = 0
                cc = 0


        wb_n.save(new_file)
        print("save file:", new_file)
        wb_n.close()
        app.quit()
    except Exception as e:
        print("run failed:", e)
        app.quit()



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    if len(sys.argv) != 5:
        exit(0)
    if sys.argv[1] == 'all':

        files = get_files_by_dir('./')
        print(files)
        for file in files:
            file_process(file, sys.argv[2], sys.argv[3], sys.argv[4])

    else:
        file_process(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])


