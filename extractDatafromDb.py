#!/depot/Python-2.7.9/bin/python
import sys
import os
import argparse
import sqlite3
import time
import math
import numpy as np
import xlsxwriter
from argparse import RawTextHelpFormatter

def scaleFunc(baseCol,scaleCol):
    baseCol_max = abs(max(baseCol))
    scaleCol_max = abs(max(scaleCol))
    if scaleCol_max != 0:
       scale_factor = baseCol_max//scaleCol_max + 1
    else:
       scale_factor = 1 
    return scale_factor 

def createChart(data,y_num,col_name_list,table_nm,chart1,sheet1,x_num=None):
       data_num = len(data)
       for i in range(len(y_num)):
          if x_num is not None:
             x_title = col_name_list[x_num] 
          else: 
             x_title = "numbers"
          y_title = col_name_list[y_num[i]] 

          chart1.add_series(
                  {'name':[table_nm,0,y_num[i]],
                   'values':[table_nm,1,y_num[i],data_num,y_num[i]]})
                   #'categories':[table_nm,1,x_num,data_num,x_num],
       chart1.set_title({'name':'Results of analysis'})
       chart1.set_size({'width': 800,'height':300})
       #chart1.set_x_axis({'name':x_title})
       chart1.set_y_axis({'name':y_title})
       sheet1.insert_chart('D2',chart1,{'x_offset':25,'y_offset':10})
    

def main():
    parser = argparse.ArgumentParser(description='Extract Data From SQLite database File.',formatter_class=RawTextHelpFormatter)
    parser.add_argument("-db", "--db_file", action='append', 
                   help='database file name \n'
                        'Default=[]',default=[])
    parser.add_argument( "-t", "--table_name", action='append', 
                   help='table name\n'
                        'Default=[]', default=[]  )   
    parser.add_argument( "-dm", "--data_mining", action='store', 
                   help='optional data mining control to output data excel files\n'
                        'Default=False', default="False" )   
    parser.add_argument( "-msd", "--model_storage_data", action='store', 
                   help='optional control to output model storage ASD data for data mining, '
                        'when -dm option is true\nDefault=False', default="False" )   
    parser.add_argument( "-n", "--best_num", action='store', 
                   help='number of best cost models\n'
                        'Default=100', default=100 )   
    parser.add_argument( "-d", "--min_dist_percent", action='store', 
                   help='min parameter coordinates point distance percentage used to classify the unique best cost models\n'
                        'Default=5', default=5 )   
    args = parser.parse_args()

    db_list = args.db_file
    all_data_table =dict()
    all_data = list()
    col_name_list_back = list()
    all_table_best_cost=dict()
    table_col_name_list_dict = dict()
    for db_file_in in db_list:  
       (db_dir_rel,db_file)=os.path.split(db_file_in)
       input_dbName = db_file_in.replace(".db","")
       out_excel_name = input_dbName+".xlsx"
       if args.data_mining.upper()=="TRUE": 
          wb = xlsxwriter.Workbook(out_excel_name)

       #Chart index parameters setting
       y_num=[2,4]
       y_num_new = [tuple+2 for tuple in y_num]
   
       table_nm_list = args.table_name
       con = sqlite3.connect(db_file_in)
       cur = con.cursor()
       col_dict_map = dict() 
       col_dict_map_title = dict() 
       cost_name_list = list()
       cost_name_global = None   
       param_init_value_dict = dict()   
       # cost name detection,dict format:{internal_cost_name:model_cost_name} 
       cur.execute('SELECT * from ModelCost')
       model_cost_col_name_list = [tuple[0] for tuple in cur.description]
       data_model_cost = cur.fetchall()
       if "model_cost_id" in model_cost_col_name_list:
          model_cost_id_index = model_cost_col_name_list.index("model_cost_id") 
          if "model_cost_name" in model_cost_col_name_list:
             model_cost_name_index = model_cost_col_name_list.index("model_cost_name")
             for d_line in data_model_cost:
                col_dict_map_title["c"+str(d_line[model_cost_id_index])]=d_line[model_cost_name_index]
                col_dict_map["c"+str(d_line[model_cost_id_index])]="c"+str(d_line[model_cost_id_index])+" AS " + str(d_line[model_cost_name_index])
                cost_name_list.append(d_line[model_cost_name_index])


       # table name detection,dict format:{model_name:model_id} 
       model_table_id_dict=dict()
       cur.execute('SELECT * from Model')
       model_col_name_list = [tuple[0] for tuple in cur.description]
       data_model = cur.fetchall()
       if "model_id" in model_col_name_list:
          model_id_index = model_col_name_list.index("model_id") 
          if "model_name" in model_col_name_list:
             model_name_index = model_col_name_list.index("model_name")
             for d_line in data_model:
                model_table_id_dict[d_line[model_id_index]]=d_line[model_name_index]

       # regression parameter name detection,dict format:{internal_param_name:parameter_name} 
       cur.execute('DROP VIEW IF EXISTS tempParam') 
       cur.execute('CREATE VIEW tempParam AS SELECT * FROM ModelParam JOIN RegressionParam ON ModelParam.model_param_id = RegressionParam.model_param_id')
       cur.execute('SELECT * FROM tempParam')
       reg_param_name_list = [tuple[0] for tuple in cur.description]
       param_data = cur.fetchall() 
       if "model_param_name" in reg_param_name_list:
          model_param_name_index = reg_param_name_list.index("model_param_name")
          if "regression_param_id" in reg_param_name_list: 
             reg_param_id_index = reg_param_name_list.index("regression_param_id")
             for p_line in param_data:
                col_dict_map_title["p"+str(p_line[reg_param_id_index])]=p_line[model_param_name_index] 
                col_dict_map["p"+str(p_line[reg_param_id_index])]="p"+str(p_line[reg_param_id_index])+" AS "+ str(p_line[model_param_name_index]) 
                if "init_value" in reg_param_name_list:
                   param_init_value_index = reg_param_name_list.index("init_value")
                   param_init_value_dict[p_line[model_param_name_index]]=float(p_line[param_init_value_index])
       table_nm_list_sort = list()
       model_id_list = model_table_id_dict.keys()  
       model_id_list.sort() 
       for id in model_id_list:
          for t_nm in table_nm_list:
             if not t_nm.find(model_table_id_dict[id]) < 0:
                table_nm_list_sort.append(t_nm)
               
       table_nm_list_sort_new = list(set(table_nm_list_sort)) 
       table_nm_list_sort_new.sort(key = table_nm_list_sort.index) 
       for table_nm in table_nm_list_sort_new:
          table_nm_new = list(table_nm)
          if len(table_nm) > 30:
             table_nm_sheet = table_nm.replace("GlobalOptimization","G")
          else:
             table_nm_sheet = table_nm 
          del table_nm_new[-1]
          table_nm_rg = "".join(table_nm_new) 
          
          cur.execute('SELECT * from %s'%table_nm)
          col_name_list = [tuple[0] for tuple in cur.description]

          if args.data_mining.upper()=="TRUE": 
             print "Creating worksheet for %s"%table_nm_sheet
             sheet1 = wb.add_worksheet(table_nm_sheet)
             sheet1_min = wb.add_worksheet(table_nm_sheet+"_MIN_COST")
             sheet1_sort = wb.add_worksheet(table_nm_sheet+"_Sort")
             chart1 = wb.add_chart({'type':'line'})
             chart1_min = wb.add_chart({'type':'line'})
             #chart1_sort = wb.add_chart({'type':'line'})
 
             for i in range(0,len(col_name_list)):
                sheet1.write(0,i,col_name_list[i]) 
                #sheet1_min.write(0,i,col_name_list[i]) 
                sheet1_sort.write(0,i,col_name_list[i]) 
          
          data = cur.fetchall()
          if not table_col_name_list_dict.has_key(input_dbName):
             table_col_name_list_dict[input_dbName] = col_name_list
             all_data_table[input_dbName]=data
          else:
             pre_col_name_list=list(table_col_name_list_dict[input_dbName])
             pre_data_table = list(all_data_table[input_dbName])
             pre_data_struct = dict()
             for i in range(0, len(col_name_list)):
                if col_name_list[i] not in pre_col_name_list: 
                   pre_col_name_list.append(col_name_list[i])
                   pre_data_struct[i]=len(pre_col_name_list)-1
             table_col_name_list_dict[input_dbName]=list(pre_col_name_list)
             new_data = list()
             index_sort_list = pre_data_struct.keys()
             index_sort_list.sort() 
             iteration_index = pre_col_name_list.index("iteration") 
             best_cost_line = list()
             for line in pre_data_table:
                new_line=list(line)
                for k in index_sort_list:
                   new_line.append(param_init_value_dict[col_name_list[k]])
                if int(new_line[iteration_index]) == -1:
                   best_cost_line = new_line
                new_data.append(new_line)
             if len(best_cost_line) == 0:
                best_cost_line = new_data[-1] 
             for line in data:
                new_line = list() 
                for i in range(0,len(pre_col_name_list)):
                   if pre_col_name_list[i] not in col_name_list:
                     new_line.append(best_cost_line[i])
                   else:
                     new_line.append(line[col_name_list.index(pre_col_name_list[i])])  
                new_data.append(new_line)       
             all_data_table[input_dbName]=new_data
               
           
          cost_index = None
          iter_index = None
          task_index = None
          for cost_name in cost_name_list:
            if cost_name in col_name_list:
               cost_index = col_name_list.index(cost_name) 
               cost_name_global = cost_name
               break
          if "iteration" in col_name_list:
             iter_index = col_name_list.index("iteration") 
          data_col_dict=dict()
          data_col_iter_dict=dict()
          iter_list = list()
          cost_dict = dict() 
          l = 1
          for line in data:
             c = 0
             for col in line:
                if data_col_dict.has_key(c):
                   data_col_dict[c].append(line[c])
                else:
                   data_col_dict[c]=[line[c]] 
                if c == cost_index:
                   if cost_dict.has_key(line[c]):
                      cost_dict[line[c]].append(line)
                   else:
                      cost_dict[line[c]]=[line] 
                if args.data_mining.upper()=="TRUE": 
                   sheet1.write(l,c,line[c])
                c += 1 
             l += 1
          if args.data_mining.upper()=="TRUE": 
             createChart(data,[2],col_name_list,table_nm_sheet,chart1,sheet1)

          col_dict_map["regression_step"]="regression_step AS iteration"

          ###MIN cost table
          if args.data_mining.upper()=="TRUE": 
             print "Creating MIN_COST worksheet for %s"%table_nm_sheet
          reg_id = 0
          cur.execute('SELECT * from  Regression')
          reg_data = cur.fetchall()
         
          for line in reg_data:
             if str(line[1])==table_nm_rg:
                reg_id = line[0]   
          if reg_id > 0: 
             reg_table_nm = "RegressionInstance"+str(reg_id)
             cur.execute('SELECT * from %s'%reg_table_nm)
             reg_int_col_name_list = [tuple[0] for tuple in cur.description]
             col_line = ["time", "task"]                      
             for reg_col_name in reg_int_col_name_list:
                if col_dict_map.has_key(reg_col_name):
                   col_line.append(col_dict_map[reg_col_name])  
             col_line_string=",".join(col_line)
             cur.execute('SELECT %s FROM %s WHERE regression_step=-1'%(col_line_string,reg_table_nm)) 
             col_name_list_min = [tuple[0] for tuple in cur.description]
             if "task" in col_name_list_min:
                task_index = col_name_list_min.index("task") 
             else:
                task_index = 9999

             data_min = cur.fetchall()
             if args.data_mining.upper()=="TRUE": 
                sheet1_min.write(0,0,"ModelStorageData") 
                for i in range(0,len(col_name_list_min)):
                   sheet1_min.write(0,i+1,col_name_list_min[i]) 
         
             for line_min in data_min:
                i = 0
                for col_iter in line_min:
                   if data_col_iter_dict.has_key(i):
                      data_col_iter_dict[i].append(line_min[i])
                   else:
                      data_col_iter_dict[i]=[line_min[i]] 
                   i += 1
             cost_index += 1
             l = 1
             for line in data_min:
                c = 0 
                for col in line:
                   c_tmp = c + 1 
                   if c != cost_index and c_tmp in y_num_new:
                      scale_factor = scaleFunc(data_col_iter_dict[cost_index],data_col_iter_dict[c])
                      col = col * scale_factor                
                   if args.data_mining.upper()=="TRUE": 
                      sheet1_min.write(l,c+1,col)
                   c += 1 
                l += 1
             col_name_list_min_new=list()
             col_name_list_min_new.append("ModelStorageData")
             col_name_list_min_new.extend(col_name_list_min)    
             
             if args.data_mining.upper()=="TRUE": 
                createChart(data_min,y_num_new,col_name_list_min_new,table_nm_sheet+"_MIN_COST",chart1_min,sheet1_min)

             col_merge_list = list()

             cur.execute("SELECT * from RegressionInstance%s"%reg_id)
             col_name_list_rin = [tuple[0] for tuple in cur.description]
             #col_merge_list.extend(col_name_list_rin)  
             col_merge_list.append("task")

             cur.execute("SELECT * from MeasurementType")
             mtype_data = cur.fetchall()
             mtype_map_dict=dict()
             for line_mtype in mtype_data:
                 mtype_map_dict["m"+str(line_mtype[0])]=line_mtype[1]
             cur.execute("SELECT * from RegressionInstanceResult%s"%reg_id)
             col_name_list_mtype = [tuple[0] for tuple in cur.description]

             for nm in col_name_list_mtype:
                 if mtype_map_dict.has_key(nm):
                    col_dict_map[nm] = nm+" AS "+ mtype_map_dict[nm]


             cur.execute("SELECT * from GaugeMeasAttr")
             col_name_list_m = [tuple[0] for tuple in cur.description]
             col_merge_list.extend(col_name_list_m) 
             col_merge_list.extend(col_name_list_mtype)
            
             col_merge_update_list = list()
             for k in col_merge_list:
                if col_dict_map.has_key(k):
                   col_merge_update_list.append(col_dict_map[k])
                else:
                   col_merge_update_list.append(k)
             col_merge_update_list.remove("regression_instance_id") 
             col_merge_update_list.remove("meas_id")
             col_reg_int_str = ",".join(col_merge_update_list)
       
             ####Add model storage table #####
             if args.data_mining.upper()=="TRUE" and args.model_storage_data.upper()=="TRUE": 
                print "Adding model storage data worksheet for %s_MIN_COST"%table_nm_sheet
                min_task_list = list()
                if task_index < len(data_col_iter_dict):
                   min_task_list = data_col_iter_dict[task_index] 
                cur.execute('DROP VIEW IF EXISTS ASDFile') 
                cur.execute('CREATE VIEW ASDFile AS SELECT * FROM RegressionInstance%s JOIN RegressionInstanceResult%s USING(regression_instance_id) JOIN GaugeMeasAttr USING(meas_id)'%(reg_id,reg_id))
                #min_task_list=list(set(min_task_list))
                min_task_list_tmp = list()   
                row_line_no = 1
                for t in min_task_list:
                   table_nm_short = table_nm
                   #table_nm_short = table_nm_short.replace("Optimization","Opt")
                   asd_name = table_nm_short+"_T"+str(t)    
                   if t not in min_task_list_tmp:
                      min_task_list_tmp.append(t)
                      cur.execute('SELECT %s FROM ASDFile WHERE task=%s'%(col_reg_int_str, t))  
                      asd_data = cur.fetchall() 
                      asd_col_name_list = [tuple[0] for tuple in cur.description]
                      cmd = "sheet_"+str(t)+"=wb.add_worksheet(asd_name)"
                      exec cmd 
                      cmd = "sheet_"+str(t)+".write_formula(0,0,'HYPERLINK("+'"#'+table_nm_sheet+"_MIN_COST!A"+str(row_line_no+1)+'"'+")')"
                      exec cmd
                      gauge_id_index = asd_col_name_list.index("gauge_id")
                      for i in range(1,len(asd_col_name_list)):
                         cmd = "sheet_"+str(t)+".write(1,i-1,asd_col_name_list[i])"
                         exec cmd
                   cmd = "sheet1_min.write_formula(row_line_no,0,'HYPERLINK("+'"#'+asd_name+"!A1"+'"'+")')"
                   exec cmd
                   row_line_no += 1

                   l=2
                   gauge_id_list = list() 
                   for line in asd_data:
                      c = 0
                      gauge_id = line[gauge_id_index]
                      if gauge_id not in gauge_id_list:
                         gauge_id_list.append(gauge_id) 
                         for col in line[1:]:
                            cmd = "sheet_"+str(t)+".write(l, c,col)"     
                            exec cmd
                            c += 1
                         l += 1

          #sort table
          cost_sort_list = cost_dict.keys()
          cost_sort_list.sort()

          if args.data_mining.upper()=="TRUE": 
             print "Creating sorted cost worksheet for %s"%table_nm_sheet
             l = 1
             for cost in cost_sort_list:
                for line in cost_dict[cost]:
                   c = 0
                   for col in line:
                      sheet1_sort.write(l,c,line[c])
                      c += 1
                   l += 1 
       if args.data_mining.upper()=="TRUE": 
          wb.close()
    i_start = 0 
    
    all_col_name_list = list()
    for k,v in table_col_name_list_dict.iteritems():
       if i_start == 0:
          i_start += 1
          all_col_name_list = v
          all_data = all_data_table[k]
       else:      
          same_sign = 1
          for i in range(0,len(v)):
             if v[i]!=all_col_name_list[i]:
                same_sign = 0  
          if same_sign == 1:  
             all_data.extend(all_data_table[k])
          else:
             raise ValueError('The UMD data columns are not same, can not merge together!')
    #best cost filter
    if len(all_data) > 0:
       round_num = 2 
       parameter_start_num = 2
       for i in range(0,len(all_col_name_list)):
          if all_col_name_list[i] in param_init_value_dict.keys():
             parameter_start_num=i   
             break
       cost_dict_in = dict() 
       data_dict_in = dict() 
       col_name_list_back = all_col_name_list
       cost_index_in = col_name_list_back.index(cost_name_global)
       for line in all_data:
          if cost_dict_in.has_key(line[cost_index_in]):
             cost_dict_in[line[cost_index_in]].append(line)
          else:
             cost_dict_in[line[cost_index_in]]=[line] 
       data_np=np.array(all_data)
       for i in range(2,len(col_name_list_back)):
          d_np_tmp = data_np[:,i]
          d_np = d_np_tmp.astype("float") 
          d_np_rd = np.around(d_np,decimals=round_num)
          unique_list = np.unique(d_np_rd).astype("U32")
           
          data_dict_in[col_name_list_back[i]]=[d_np_rd.min(),d_np_rd.max(),unique_list.tolist()]
       # dist tol calculation and parameter min/max/unique list output
       dist_value = 0
       if args.data_mining.upper()=="TRUE": 
          parameter_file_name = "parameter_info_list.txt"
          param_file = open(parameter_file_name, 'w') 
       for k,v in data_dict_in.iteritems():
          if args.data_mining.upper()=="TRUE": 
             out_line = k + ": " + str(v[0])+ " " + str(v[1]) + " point_num=" + str(len(v[2]))+"\n"
             param_file.write(out_line)  
             out_line = " ".join(v[2]) + "\n" 
             param_file.write(out_line)  
          if k in param_init_value_dict.keys():
             dist_value += (float(v[1])-float(v[0]))*(float(v[1])-float(v[0]))
       if args.data_mining.upper()=="TRUE": 
          param_file.close()
       if float(args.min_dist_percent) > 100 or float(args.min_dist_percent) <= 0:
          dist_percent = 5
       else:
          dist_percent = float(args.min_dist_percent)    
       dist_tol = math.sqrt(dist_value)*dist_percent*0.01 

       cost_sort_in_list = cost_dict_in.keys()
       cost_sort_in_list.sort()

       l = 1
       sorted_table_list =list()
       uni_min_table_list =list()
       for cost in cost_sort_in_list:
          for line in cost_dict_in[cost]:
             if l == 1:
                uni_min_table_list.append(line)
             else:
                sorted_table_list.append(line)
             l+=1
          
       list_start_index = parameter_start_num
       list_end_index = len(col_name_list_back)-1
       if args.data_mining.upper()!="TRUE":
          best_cost_out_filename = "all_output.csv"
          best_cost_file = open(best_cost_out_filename, 'w') 
          out_line =",".join(col_name_list_back)+"\n"
          min_best_cost_out_filename = "best_output.csv"
          min_best_cost_file = open(min_best_cost_out_filename, 'w') 
          min_out_line =",".join(col_name_list_back)+"\n"
          best_cost_file.write(out_line)
          min_best_cost_file.write(min_out_line)
          iter_index = col_name_list_back.index("iteration")
          for sort_line in sorted_table_list:
             np_line = np.array(sort_line)
             str_line = np_line.astype("U32").tolist()
             out_line =",".join(str_line)+"\n"
             best_cost_file.write(out_line)
             sort_line_list=list(sort_line)
             if sort_line_list[iter_index] == -1:   
                min_best_cost_file.write(out_line)
          best_cost_file.close() 
          min_best_cost_file.close() 
       for sort_line in sorted_table_list:
          if len(uni_min_table_list) >= int(args.best_num):
             break
          tmp_sort_list = sort_line[list_start_index:list_end_index]
          tmp_sort_array = np.array(tmp_sort_list)
          append_sign = 1
          for uni_line in uni_min_table_list:
             tmp_uni_list = uni_line[list_start_index:list_end_index]
             tmp_uni_array = np.array(tmp_uni_list)
             tmp_diff = tmp_uni_array-tmp_sort_array
             tmp_diff_sqrt = np.square(tmp_diff)
             dist = math.sqrt(tmp_diff_sqrt.sum()) 
             if dist < float(dist_tol):
                append_sign = 0
                break
          if append_sign == 1 and len(uni_min_table_list) < int(args.best_num):
             uni_min_table_list.append(sort_line)

       # output the best cost to the file 
       if args.data_mining.upper()=="TRUE":
          best_cost_out_filename = "best_unique_cost_output.csv"
          best_cost_file = open(best_cost_out_filename, 'w') 
          #out_line ="Filter dist tolerance:"+str(dist_tol)+"\n"
          #best_cost_file.write(out_line)
          print_line_list=["Name"]
          time_index = col_name_list_back.index("time")
          del col_name_list_back[time_index]
          iter_index = col_name_list_back.index("iteration")
          del col_name_list_back[iter_index]
          print_line_list.extend(col_name_list_back)
          out_line =",".join(print_line_list)+"\n"
          best_cost_file.write(out_line)
          kernelN_index = None
          if "KernelNumber" in col_name_list_back:
             kernelN_index = col_name_list_back.index("KernelNumber")
          i = 1
          for line in uni_min_table_list:
             line_new = ["R"+str(i)] 
             line_list = list(line)
             del line_list[time_index]
             del line_list[iter_index]
             if kernelN_index is not None:
                line_list[kernelN_index]=int(line_list[kernelN_index])
             line_new.extend(line_list)  
             np_line = np.array(line_new)
             str_line = np_line.astype("U32").tolist()
             out_line = ",".join(str_line) + "\n"
             best_cost_file.write(out_line)
             i+=1
          best_cost_file.close()
    
  
if(__name__ == "__main__"):
    main()
    sys.exit(0)
                    
