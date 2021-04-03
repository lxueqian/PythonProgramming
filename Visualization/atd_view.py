from tornado.ioloop import IOLoop
from bokeh.layouts import widgetbox, row, column,layout
from bokeh.models import ColumnDataSource, Slider, RangeSlider, DataRange1d, Div, CustomJS, HoverTool,Range1d
from bokeh.models.widgets import DataTable, TableColumn, Tabs, Panel, MultiSelect, Select, Button, RadioGroup
from bokeh.plotting import figure
from bokeh.server.server import Server
import numpy as np
import json
import copy
import math
from bokeh.io import curdoc
from bokeh.models.renderers import GlyphRenderer

import sys
sys.path.append('.')
sys.path.append('..')

from trajectory import get_trajectory_list_for_plot,get_md_point,get_tl_dls_lpdis_kop, get_sliding_rate
import unit_conversion_utility as unit_util


def define_plots(original_traj_data, trajectories, kpi_names, kpi_values, is_metric_unit, azi):
    hover = HoverTool(tooltips=[])

    for name in kpi_names:
        hover.tooltips.append((name, "@" + name + "{0.00}"))

    plot_v = figure(toolbar_location='above', title='Vertical View', plot_height=500, plot_width=500,
                    background_fill_color="white", output_backend="webgl", match_aspect=True)
    
    plot_v.y_range = DataRange1d(flipped=True)
    plot_v.add_tools(hover)
    # plot_v.toolbar.active_inspect = None  # Inactive hover in toolbar

    plot_h = figure(toolbar_location='above', title='Horizontal View', plot_height=500, plot_width=500,
                    background_fill_color="white", output_backend="webgl", match_aspect=True)
    
    plot_h.add_tools(hover)
    # plot_h.toolbar.active_inspect = None  # Inactive hover in toolbar

    if is_metric_unit:
        plot_v.xaxis.axis_label = 'vsec (m)'
        plot_v.yaxis.axis_label = 'tvd (m)'
        plot_h.xaxis.axis_label = 'ew (m)'
        plot_h.yaxis.axis_label = 'ns (m)'
    else:
        plot_v.xaxis.axis_label = 'vsec (ft)'
        plot_v.yaxis.axis_label = 'tvd (ft)'
        plot_h.xaxis.axis_label = 'ew (ft)'
        plot_h.yaxis.axis_label = 'ns (ft)'

    vsec_list = []
    tvd_list = []
    ew_list = []
    ns_list = []
    dict_hover = dict()
    for i in range(len(trajectories)):
        md, tvd, ns, ew, vsec = get_trajectory_list_for_plot(trajectory_dict_list = trajectories[i]['Stations'],azimuth = azi) ##use trajectory
        if is_metric_unit:
            vsec_list.append(vsec)
            tvd_list.append(tvd)
            ew_list.append(ew)
            ns_list.append(ns)

        else:
            vsec_list.append([unit_util.meter_to_foot(val) for val in vsec])
            tvd_list.append([unit_util.meter_to_foot(val) for val in tvd])
            ew_list.append([unit_util.meter_to_foot(val) for val in ew])
            ns_list.append([unit_util.meter_to_foot(val) for val in ns])

    # Set sources needed by hover
    for idx in range(len(kpi_names)):
        dict_hover[kpi_names[idx]] = []
        for i in range(len(kpi_values)):
            dict_hover[kpi_names[idx]].append(kpi_values[i][idx])

    v_full_data = {**dict(vsec=vsec_list, tvd=tvd_list), **dict_hover}
    h_full_data = {**dict(ew=ew_list, ns=ns_list), **dict_hover}

    v_source = ColumnDataSource(v_full_data)
    h_source = ColumnDataSource(h_full_data)

    plot_v.multi_line(xs="vsec", ys="tvd", source=v_source,line_width=2)
    plot_h.multi_line(xs="ew", ys="ns", source=h_source,line_width=2)

    vsec = []
    tvd = []
    ew = []
    ns = []
    full_data_md = {**dict(vsec=vsec, tvd=tvd, ew=ew, ns=ns)}
    source_md = ColumnDataSource(full_data_md)      
             
    plot_v.circle(x="vsec", y="tvd", source=source_md, size=8, color="navy", alpha=0.5,name='p1')
    plot_h.circle(x="ew", y="ns", source=source_md, size=8, color="navy", alpha=0.5,name='p1')
    
    if original_traj_data:
        md_original, tvd_original, ns_original, ew_original, vsec_original = get_trajectory_list_for_plot(trajectory_dict_list=original_traj_data['Stations']) 
        
        original_vsec_list,origianl_tvd_list,original_ew_list,origianl_ns_list=[],[],[],[]
        if is_metric_unit:
            original_vsec_list.append(vsec_original)
            origianl_tvd_list.append(tvd_original)
            original_ew_list.append(ew_original)
            origianl_ns_list.append(ns_original)

        else:
            original_vsec_list.append([unit_util.meter_to_foot(val) for val in vsec_original])
            origianl_tvd_list.append([unit_util.meter_to_foot(val) for val in tvd_original])
            original_ew_list.append([unit_util.meter_to_foot(val) for val in ew_original])
            origianl_ns_list.append([unit_util.meter_to_foot(val) for val in ns_original])
            
        original_full_data =  {**dict(vsec=original_vsec_list, tvd=origianl_tvd_list, ew=original_ew_list, ns=origianl_ns_list)}
        source_original_data = ColumnDataSource(original_full_data) 
        plot_v.multi_line(xs="vsec", ys="tvd", source=source_original_data,line_width=2,line_color="#FD9F6C")
        plot_h.multi_line(xs="ew", ys="ns", source=source_original_data,line_width=2,line_color="#FD9F6C")
        print('000000')
    return plot_v, plot_h, v_source, v_full_data, h_source, h_full_data, full_data_md, source_md


# define SlidingRate-MD Distribution plot
def SR_MD_distribution_plots(x=[],y=[]):
    hover = HoverTool(tooltips=[])
    hover.tooltips = [("MD","@MD{0.00}"), ("SlidingRate","@SlidingRate{0.00}")]
    
    plot_md_sr = figure(toolbar_location='above', title='SR-MD Distribution', plot_height=200, plot_width=1000,
                    background_fill_color="white", output_backend="webgl", match_aspect=True)
    
    plot_md_sr.xaxis.axis_label = 'MD'
    plot_md_sr.yaxis.axis_label = 'SlidingRate'
    
    plot_md_sr.add_tools(hover)
    # plot_md_sr.toolbar.active_inspect = None  # Inactive hover in toolbar
    
    plot_md_sr_full_data = {**dict(MD=x, SlidingRate=y)}
    plot_md_sr_source = ColumnDataSource(plot_md_sr_full_data)   
    
    plot_md_sr.vbar(x='MD',top='SlidingRate',source=plot_md_sr_source,width=10,fill_color='darkmagenta',line_color="white")
    # plot_md_sr.line(x='MD',y='SlidingRate',source=plot_md_sr_source,line_width=1, line_color ="royalblue")
    plot_md_sr.y_range.start = -10
    plot_md_sr.y_range.end = 100
    
    return plot_md_sr, plot_md_sr_source

# define ToolFace-MD Distribution plot
def TF_MD_distribution_plots(x=[],y=[]):
    hover = HoverTool(tooltips=[])
    hover.tooltips = [("MD","@MD{0.00}"), ("ToolFace","@ToolFace{0.00}")]
    
    plot_md_tf = figure(toolbar_location='above', title='TF-MD Distribution', plot_height=200, plot_width=1000,
                    background_fill_color="white", output_backend="webgl", match_aspect=True)
    
    plot_md_tf.xaxis.axis_label = 'MD'
    plot_md_tf.yaxis.axis_label = 'ToolFace'
    
    plot_md_tf.add_tools(hover)
    # plot_md_tf.toolbar.active_inspect = None  # Inactive hover in toolbar
    
    plot_md_tf_full_data = {**dict(MD=x, ToolFace=y)}
    plot_md_tf_source = ColumnDataSource(plot_md_tf_full_data)   
    
    plot_md_tf.vbar(x='MD',top='ToolFace',source=plot_md_tf_source,width=15,fill_color='darkmagenta',line_color="white")
    plot_md_tf.line(x='MD',y='ToolFace',source=plot_md_tf_source,line_width=1, line_color ="royalblue")
    plot_md_tf.y_range.start = -180
    plot_md_tf.y_range.end = 360
    
    return plot_md_tf, plot_md_tf_source

def define_table(trajectories, is_metric_unit):
    source = ColumnDataSource(dict())  #
    index_list = np.arange(len(trajectories))
    source.data = get_table_source_data(trajectories, index_list, is_metric_unit)

    # Change units displayed in titles
    if is_metric_unit:
        columns = [
            TableColumn(field="comment", title="Comment"),
            TableColumn(field="md", title="MD (m)"),
            TableColumn(field="incl", title="Inclination (deg)"),
            TableColumn(field="azim", title="Azimuth (deg)"),
            TableColumn(field="tvd", title="TVD (m)"),
            TableColumn(field="ns", title="NS (m)"),
            TableColumn(field="ew", title="EW (m)"),
            TableColumn(field="dls", title="DLS (deg/30m)")
        ]
    else:
        columns = [
            TableColumn(field="comment", title="Comment"),
            TableColumn(field="md", title="MD (ft)"),
            TableColumn(field="incl", title="Inclination (deg)"),
            TableColumn(field="azim", title="Azimuth (deg)"),
            TableColumn(field="tvd", title="TVD (ft)"),
            TableColumn(field="ns", title="NS (ft)"),
            TableColumn(field="ew", title="EW (ft)"),
            TableColumn(field="dls", title="DLS (deg/100ft)")
        ]
    table = DataTable(source=source, columns=columns, width=1000, height=250)

    return table, source

def define_multi_select(kpi_values,trajectories):
    options = []
    num = len(trajectories)
    # Considering two cases: whether KpiList exsits
    if kpi_values != []:
        for i in range(num):
            label = str(i) + ") "

            for value in kpi_values[i]:
                label += str(round(value, 2)) + ", "
            options.append(label)
    else:
        for i in range(num):
            label = str(i) + ") "
            label += str(round(trajectories[i]['Stations'][-1]['MD'],2))
            
            options.append(label)
            
    return MultiSelect(value=options, options=options, size=25), options

def define_range_slider_kpi(kpi_names, kpi_values):
    sliders = []
    if len(kpi_names) != 0:
        tol = 1e-6  # To give a range for slider display
        max_kpis = np.amax(kpi_values, axis=0)
        min_kpis = np.amin(kpi_values, axis=0)

        for i in range(len(kpi_names)):
            slider = RangeSlider(start=min_kpis[i], end=max_kpis[i] + tol, value=(min_kpis[i], max_kpis[i] + tol),
                                 step=(max_kpis[i] - min_kpis[i]) / 100,
                                 width=250, title=kpi_names[i], orientation="horizontal", callback_policy='mouseup')
            sliders.append(slider)

    return sliders

def define_md_slider(total_length=1,step=1):
    slider_md = Slider(start = 0, end = total_length, value = 0,step = step,
                        width=250, title='MD', orientation="horizontal", callback_policy='mouseup')
    return slider_md

def get_kpi_list(trajectories, is_metric_unit):
    kpi_names = []
    kpi_values = []  # Store as [trajectory number][kpi number]

    if len(trajectories) > 0:
        if 'KpiList' in trajectories[0].keys():
            kpi_names = list(trajectories[0]['KpiList'].keys())    
               
            for traj in trajectories: #if trajectories are empty then this loop won't start
                kpis = list(traj['KpiList'].values())
                kpi_values.append([convert_kpi_unit(kpis[i], kpi_names[i], is_metric_unit) for i in range(len(kpis))])

    return kpi_names, kpi_values


def convert_kpi_unit(value_si, name, is_metric_unit):
    if is_metric_unit:  # Metric unit system
        if "dls" in name.lower():
            value = unit_util.radian_per_meter_to_degree_per_thirty_meters(value_si)
        else:
            value = value_si  # Assume length measurement
    else:  # English unit system
        if "dls" in name.lower():
            value = unit_util.radian_per_meter_to_degree_per_hundred_feet(value_si)
        else:
            value = unit_util.meter_to_foot(value_si)  # Assume length measurement

    return value


def get_index_list_from_sliders(kpi_values, slider_ranges):
    tol = 1e-6
    index_list = []

    traj_number, kpi_number = np.shape(kpi_values)
    for traj_idx in range(0, traj_number):
        is_in_range = True
        kpi_idx = 0
        while kpi_idx < kpi_number and is_in_range:
            if not (slider_ranges[kpi_idx][0] - tol <= kpi_values[traj_idx][kpi_idx] <= slider_ranges[kpi_idx][1] + tol):
                is_in_range = False
                break
            kpi_idx += 1

        if is_in_range:
            index_list.append(traj_idx)

    return index_list


def update_plots_source_data(source_data, index_list):
    updated_data = dict()
    for key in source_data:
        updated_data[key] = [source_data[key][i] for i in index_list]

    return updated_data


def get_table_source_data(trajectories, index_list, is_metric_unit):
    if index_list is None or len(index_list) != 1:
        table_data = dict()
    else:
        stations = trajectories[index_list[0]]['Stations']
        comment = []
        md = []
        incl = []
        azim = []
        tvd = []
        ns = []
        ew = []
        dls = []

        for station in stations:
            comment.append(station['Comment'])
            incl.append(round(unit_util.radian_to_degree(station['Inclination']), 2))
            azim.append(round(unit_util.radian_to_degree(station['Azimuth']), 2))
            
            if is_metric_unit:  # Metric unit system
                md.append(round(station['MD'], 2))
                tvd.append(round(station['TVD'], 2))
                ns.append(round(station['NS'], 2))
                ew.append(round(station['EW'], 2))
                val = unit_util.radian_per_meter_to_degree_per_thirty_meters(station['DLS'])
                if val > 1e8:
                    val = 0
                dls.append(round(val, 2))
            else:  # English unit system
                md.append(round(unit_util.meter_to_foot(station['MD']), 2))
                tvd.append(round(unit_util.meter_to_foot(station['TVD']), 2))
                ns.append(round(unit_util.meter_to_foot(station['NS']), 2))
                ew.append(round(unit_util.meter_to_foot(station['EW']), 2))
                val = unit_util.radian_per_meter_to_degree_per_hundred_feet(station['DLS'])
                if val > 1e8:
                    val = 0
                dls.append(round(val, 2))

        table_data = dict(
            comment=comment,
            md=md,
            incl=incl,
            azim=azim,
            tvd=tvd,
            ns=ns,
            ew=ew,
            dls=dls
        )

    return ColumnDataSource(table_data).data
            
def refresh_page(trajectories, is_metric_unit, BHA, original_traj_data=[]):
    # Check if kpilist exsits, if not then calculate
    if len(trajectories) != 0 and ('KpiList' not in trajectories[0].keys()):
        for trajectory in trajectories:
            temp = {}
            total_length, dls, kop, lp_distance = get_tl_dls_lpdis_kop(trajectory['Stations'])
            temp["TotalLength"] = total_length
            temp["Dls"] = dls
            temp["Kop"] = kop
            temp["LpDistance"] = lp_distance
            trajectory['KpiList'] = temp
            print('trajectory kpilist calculation is done')
            
    # Calculate and add slidering rate kpi
    if len(trajectories) != 0 and BHA != []:
        Kpi_SR, Distribution_SR, MD_temp, TF_list  = get_sliding_rate(trajectories,BHA[0],BHA[1],BHA[2])

        for i,trajectory in enumerate(trajectories):
            trajectory['KpiList']["SlidingRate"] = Kpi_SR[i] 
            trajectory['KpiList']["MaxSlidingRate"] = max(Distribution_SR[i])
            trajectory['KpiList']["ToolFace"] = max(TF_list[i])
              
         
    # Get kpi ranges - kop, dls, td
    kpi_names, kpi_values = get_kpi_list(trajectories, is_metric_unit)

    # Define kpi sliders
    slider_kpi = define_range_slider_kpi(kpi_names, kpi_values)
        
    # Define table
    table_traj, table_source = define_table(trajectories, is_metric_unit)
    
    # Define azi slider
    slider_azi = Slider(start = 0, end = 360, value = 0,step = 360/100.0,
                        width=250, title='Azimuth', orientation="horizontal", callback_policy='mouseup')

    # Define 2D plots
    plot_v, plot_h, v_source, v_full_data, h_source, h_full_data, full_data_md, source_md = define_plots(original_traj_data,trajectories,kpi_names, kpi_values, is_metric_unit,unit_util.degree_to_radian(slider_azi.value))
        
    plot_md_sr, plot_md_sr_source = SR_MD_distribution_plots() 
    
    plot_md_tf, plot_md_tf_source = TF_MD_distribution_plots()
    
    plot_3d = widgetbox(Div(text="""Coming soon...""", width=500, height=500)) 

    # Define md slider   
    if len(v_full_data['vsec']) == 1: #case when upload one trajectory
        
        slider_md = define_md_slider(math.floor(table_source.data['md'][-1]),table_source.data['md'][-1]/100)
    else:
        slider_md = define_md_slider()

    # Define multiply selection
    multi_select, full_select_options = define_multi_select(kpi_values,trajectories)
    
    # Show information for available candidates
    multi_select.title = "Candidates: " + str(len(full_select_options)) + " available, " + str(len(full_select_options)) + " selected."

    def on_multi_select_change(attrname, old, new):
        idx = [int(item.split(")")[0]) for item in new]  
    
        # Update displayed information
        multi_select.title = "Candidates: " + str(len(multi_select.options)) + " available, " + str(len(idx)) + " selected."

        # Update table if only one is selected
        table_source.data = get_table_source_data(trajectories, idx, is_metric_unit)
        # print(table_source.data)
        
        # Update multi-lines' sources
        h_source.data = update_plots_source_data(h_full_data, idx)
        v_source.data = update_plots_source_data(v_full_data, idx)
        
        # Update md slider if only one is selected
        if table_source.data != {}:
            total_length = table_source.data['md'][-1]
            slider_md.end = math.floor(total_length)
            slider_md.step = total_length/100
            slider_md.value = 0           
            
            Kpi_SR, Distribution_SR, MD_temp, TF_list  = get_sliding_rate([trajectories[idx[0]]],BHA[0],BHA[1],BHA[2])
            MD_list = []
            for li in MD_temp[0]:
                MD_list.append(li[0])

            plot_md_sr_source.data['MD'] = MD_list
            plot_md_sr_source.data['SlidingRate'] = Distribution_SR[0]
            
            plot_md_tf_source.data['MD'] = MD_list
            plot_md_tf_source.data['ToolFace'] = TF_list[0]
        
        # slider_md default settings              
        else: 
            slider_md.end = 1
            slider_md.step = 1
            slider_md.value = 0

            plot_md_sr_source.data['MD'] = []
            plot_md_sr_source.data['SlidingRate'] = []
            plot_md_tf_source.data['MD'] = []
            plot_md_tf_source.data['ToolFace'] = []
         
        # Return md point to zero
        source_md.data = {'tvd':[], 'ns':[], 'ew':[], 'vsec':[]}  
        
        # Return slider azi to zero 
        slider_azi.value = 0
        
        # Update plots by selected MD   
        def on_slider_md_change(attrname, old, new):
            MD = new['value'][0] 
            trajectory = trajectories[idx[0]]                
            # Update circle
            md, tvd, ns, ew, vsec = get_md_point(trajectory['Stations'],MD,unit_util.degree_to_radian(slider_azi.value))       
                        
            source_md.data = {'tvd':tvd, 'ns':ns, 'ew':ew, 'vsec':vsec}   
                                
        slider_mouseup_md_source = ColumnDataSource(data=dict(value=[]))
        slider_mouseup_md_source.on_change('data', on_slider_md_change)
        slider_md.callback = CustomJS(args=dict(source=slider_mouseup_md_source), code="""
                source.data = { value: [cb_obj.value] }
            """)
        
        # Update plots by selected AZI  
        def on_slider_azi_change(attrname, old, new):
            slider_md.value = 0
            source_md.data = {'tvd':[], 'ns':[], 'ew':[], 'vsec':[]} #restore slider md to default
            azi = float(unit_util.degree_to_radian(new['value'][0]))            
            vsec_list = []
            tvd_list = []
            ew_list = []
            ns_list = []
            
            for index in idx:
                md, tvd, ns, ew, vsec = get_trajectory_list_for_plot(trajectory_dict_list=trajectories[index]['Stations'],azimuth=azi) #use trajectory
                if is_metric_unit:
                    vsec_list.append(vsec)
                    tvd_list.append(tvd)
                    ew_list.append(ew)
                    ns_list.append(ns)

                else:
                    vsec_list.append([unit_util.meter_to_foot(val) for val in vsec])
                    tvd_list.append([unit_util.meter_to_foot(val) for val in tvd])
                    ew_list.append([unit_util.meter_to_foot(val) for val in ew])
                    ns_list.append([unit_util.meter_to_foot(val) for val in ns])      

            v_source.data['vsec'] = vsec_list
            v_source.data['tvd'] = tvd_list
 
            
        slider_mouseup_azi_source = ColumnDataSource(data=dict(value=[]))
        slider_mouseup_azi_source.on_change('data', on_slider_azi_change)
        slider_azi.callback = CustomJS(args=dict(source=slider_mouseup_azi_source), code="""
                source.data = { value: [cb_obj.value] }
            """)      
        
    multi_select.on_change("value", on_multi_select_change)   
    multi_select.callback = CustomJS(args=dict(sel=multi_select), code="""
        document.getElementsByName(sel.name)[0].focus();
    """)

    # Only when kpiList exists this happen
    if kpi_names != [] and kpi_values != []:
        # Update plots, table and multi-section box by selected kpi
        def on_slider_change(attrname, old, new):
            updated_index_list = get_index_list_from_sliders(kpi_values, [item.value for item in slider_kpi])

            table_source.data = get_table_source_data(trajectories, updated_index_list, is_metric_unit)

            updated_options = [full_select_options[i] for i in updated_index_list]
            multi_select.options = updated_options
            multi_select.value = updated_options

        # This data source is just used to communicate / trigger the mouse up callback
        slider_mouseup_source = ColumnDataSource(data=dict(value=[]))
        slider_mouseup_source.on_change('data', on_slider_change)

        for slider in slider_kpi:
            slider.callback = CustomJS(args=dict(source=slider_mouseup_source), code="""
                source.data = { value: [cb_obj.value] }
            """)

    # Update plots by selected MD in case that only one trajectory in one file is uploaded 
    def on_slider_md_change(attrname, old, new):
        MD = new['value'][0] 
        trajectory = trajectories[0]           
        # Update circle
        md, tvd, ns, ew, vsec = get_md_point(trajectory['Stations'],MD,unit_util.degree_to_radian(slider_azi.value))   
            
        source_md.data = {'tvd':tvd, 'ns':ns, 'ew':ew, 'vsec':vsec}   
                   
    slider_mouseup_md_source = ColumnDataSource(data=dict(value=[]))
    slider_mouseup_md_source.on_change('data', on_slider_md_change)
    slider_md.callback = CustomJS(args=dict(source=slider_mouseup_md_source), code="""
            source.data = { value: [cb_obj.value] }
        """)
    
    # Update plots by selected AZI in case that only one trajectory in one file is uploaded 
    def on_slider_azi_change(attrname, old, new):
        slider_md.value = 0
        source_md.data = {'tvd':[], 'ns':[], 'ew':[], 'vsec':[]} #restore slider md to default       
        azi = float(unit_util.degree_to_radian(new['value'][0]))
        vsec_list = []
        tvd_list = []
        ew_list = []
        ns_list = []

        for trajectory in trajectories:
            md, tvd, ns, ew, vsec = get_trajectory_list_for_plot(trajectory_dict_list=trajectories[0]['Stations'],azimuth=azi) #use trajectory

            if is_metric_unit:
                vsec_list.append(vsec)
                tvd_list.append(tvd)
                ew_list.append(ew)
                ns_list.append(ns)

            else:
                vsec_list.append([unit_util.meter_to_foot(val) for val in vsec])
                tvd_list.append([unit_util.meter_to_foot(val) for val in tvd])
                ew_list.append([unit_util.meter_to_foot(val) for val in ew])
                ns_list.append([unit_util.meter_to_foot(val) for val in ns])
                    
        v_source.data['vsec'] = vsec_list
        v_source.data['tvd'] = tvd_list
        
    slider_mouseup_azi_source = ColumnDataSource(data=dict(value=[]))
    slider_mouseup_azi_source.on_change('data', on_slider_azi_change)
    slider_azi.callback = CustomJS(args=dict(source=slider_mouseup_azi_source), code="""
            source.data = { value: [cb_obj.value] }
        """) 
    
    # left column display considering two conditions
    if len(kpi_names) == 0:
        layout_control = column(widgetbox(multi_select),widgetbox(slider_md),widgetbox(slider_azi))
    else:
        layout_control = column(widgetbox(slider_kpi), widgetbox(multi_select),widgetbox(slider_md),widgetbox(slider_azi))
        
    tab_2d_plots = Panel(child=row(plot_v, plot_h), title="2D View")        
    tab_3d_plot = Panel(child=plot_3d, title="3D View")
    tab_plots = Tabs(tabs=[tab_2d_plots, tab_3d_plot])
    
    layout_output = column(tab_plots, table_traj,widgetbox(plot_md_sr),widgetbox(plot_md_tf))        
    return layout_control, layout_output

def show_page(doc):
    # Update trajectory data
    def on_select_file_change(attrname, old, new):
        trajectories = full_data[new]
        num = int(radio_group_BHA.active)
        BR0 = float(radio_group_BHA.labels[num].split()[1].split(':')[1])
        TR0 = float(radio_group_BHA.labels[num].split()[2].split(':')[1])
        MotorYield = float(radio_group_BHA.labels[num].split()[3].split(':')[1])
        BHA=(BR0,TR0,MotorYield)
        
        layout_control, layout_output = refresh_page(trajectories, radio_group.active == 0, BHA)
        update_layouts(layout_whole, generate_layouts(layout_control, layout_output))

    select_file = Select(title='Select data:', value="", options=[], width=250)
    select_file.on_change('value', on_select_file_change)
            
    # Change unit system
    def on_radio_group_change(attrname, old, new):
        if len(full_data) == 0:
            trajectories = []
        else:
            trajectories = full_data[select_file.value]

        num = int(radio_group_BHA.active)
        BR0 = float(radio_group_BHA.labels[num].split()[1].split(':')[1])
        TR0 = float(radio_group_BHA.labels[num].split()[2].split(':')[1])
        MotorYield = float(radio_group_BHA.labels[num].split()[3].split(':')[1])
        BHA=(BR0,TR0,MotorYield)
        
        layout_control, layout_output = refresh_page(trajectories, new == 0, BHA)
        update_layouts(layout_whole, generate_layouts(layout_control, layout_output))

    # Define radio group for unit
    radio_group = RadioGroup(labels=["Metric Unit", "English Unit"], inline=True, active=0)
    radio_group.on_change("active", on_radio_group_change)
    
    # Change BHA system
    def on_radio_group_BHA_change(attrname, old, new):    
        if len(full_data) == 0:
            trajectories = []
        else:
            trajectories = full_data[select_file.value]
                   
        num = int(radio_group_BHA.active)
        BR0 = float(radio_group_BHA.labels[num].split()[1].split(':')[1])
        TR0 = float(radio_group_BHA.labels[num].split()[2].split(':')[1])
        MotorYield = float(radio_group_BHA.labels[num].split()[3].split(':')[1])
        BHA=(BR0,TR0,MotorYield)
        
        layout_control, layout_output = refresh_page(trajectories, radio_group.active == 0, BHA)
        update_layouts(layout_whole, generate_layouts(layout_control, layout_output))
        
            
    # Define radio group for BHA
    radio_group_BHA = RadioGroup(labels=["BHA_1: BR0:1 TR0:-1 MotorYield:20", "BHA_2: BR0:1 TR0:-1 MotorYield:10", 'BHA_3: BR0:-1.5 TR0:-1 MotorYield:10',
                                         'BHA_4: BR0:1 TR0:-1 MotorYield:5', 'BHA_5: BR0:4 TR0:4 MotorYield:8'],active=0)   
    radio_group_BHA.on_change("active", on_radio_group_BHA_change) 
    
    full_data = dict()

    # Define a button for json file uploading
    def on_button_upload_file_change(attr, old, new):
        for i in range(len(new['file_contents'])):
            # Store all uploaded data with files names
            full_data[new['file_name'][i]] = new['file_contents'][i]
            
        # View the first loaded file
        select_file.value = new['file_name'][0]
        select_file.options = list(full_data.keys())
        
    source_button = ColumnDataSource({'file_contents': [], 'file_name': []})
    source_button.on_change('data', on_button_upload_file_change)

    button_upload_file = Button(label="Upload Json File", button_type="primary", width=250)
    button_upload_file.callback = CustomJS(args=dict(file_source=source_button), code="""
    function error_handler(evt) {
        if(evt.target.error.name == "NotReadableError") {
            alert("Can't read file!");
        }
    }

    var input = document.createElement('input');
    input.setAttribute('type', 'file');
    input.setAttribute('multiple', true);
    input.accept = ".json"
    input.onchange = function(){
    
        if (window.FileReader) {
            // readAsDataURL represents the file's data as a base64 encoded string
            var names = []
            var contents = []
            var txt = new String(".txt")
            for (var i = 0; i < input.files.length; i++) {
                var f = input.files[i];            
                var reader = new FileReader();
                reader.onload = (function(f) {
                    return function(evt) {
                        var b64string = evt.target.result;
                        names.push(f.name);                       
                        contents.push(JSON.parse(b64string)); 
                        if (names.length == input.files.length) {
                            file_source.data = {'file_contents' : contents, 'file_name' : names};
                        }
                    };
                })(f);
                reader.onerror = error_handler;
                reader.readAsText(f);
            }
            //file_source.data = {'file_contents' : contents, 'file_name' : names};
        } else {
            alert('FileReader is not supported in this browser');
        }
    }
    input.click();
    """)
    
    
    '''
    ==========================================================================
    Trajectory ops rectify page below
    ==========================================================================
    '''
    
    # Update trajectory data
    def on_select_file_1_change(attrname, old, new):
        trajectories = full_data_1[new]
        num = int(radio_group_BHA_1.active)
        BR0 = float(radio_group_BHA_1.labels[num].split()[1].split(':')[1])
        TR0 = float(radio_group_BHA_1.labels[num].split()[2].split(':')[1])
        MotorYield = float(radio_group_BHA_1.labels[num].split()[3].split(':')[1])
        BHA=(BR0,TR0,MotorYield)
        
        layout_control_1, layout_output_1 = refresh_page(trajectories, radio_group_1.active == 0, BHA)
        update_layouts(layout_whole_1, generate_layouts_1(layout_control_1, layout_output_1))

    select_file_1 = Select(title='Select data:', value="", options=[], width=250)
    select_file_1.on_change('value', on_select_file_1_change)
            
    # Change unit system
    def on_radio_group_1_change(attrname, old, new):
        if len(full_data_1) == 0:
            trajectories = []
        else:
            trajectories = full_data_1[select_file_1.value]

        num = int(radio_group_BHA_1.active)
        BR0 = float(radio_group_BHA_1.labels[num].split()[1].split(':')[1])
        TR0 = float(radio_group_BHA_1.labels[num].split()[2].split(':')[1])
        MotorYield = float(radio_group_BHA_1.labels[num].split()[3].split(':')[1])
        BHA=(BR0,TR0,MotorYield)
        
        layout_control_1, layout_output_1 = refresh_page(trajectories, new == 0, BHA)
        update_layouts(layout_whole_1, generate_layouts_1(layout_control_1, layout_output_1))

    # Define radio group for unit
    radio_group_1 = RadioGroup(labels=["Metric Unit", "English Unit"], inline=True, active=0)
    radio_group_1.on_change("active", on_radio_group_1_change)
    
    # Change BHA system
    def on_radio_group_BHA_1_change(attrname, old, new):    
        if len(full_data_1) == 0:
            trajectories = []
        else:
            trajectories = full_data_1[select_file_1.value]
                 
        num = int(radio_group_BHA_1.active)
        BR0 = float(radio_group_BHA_1.labels[num].split()[1].split(':')[1])
        TR0 = float(radio_group_BHA_1.labels[num].split()[2].split(':')[1])
        MotorYield = float(radio_group_BHA_1.labels[num].split()[3].split(':')[1])
        BHA=(BR0,TR0,MotorYield)
        
        layout_control_1, layout_output_1 = refresh_page(trajectories, radio_group_1.active == 0, BHA)
        update_layouts(layout_whole_1, generate_layouts_1(layout_control_1, layout_output_1))
            
    # Define radio group for BHA
    radio_group_BHA_1 = RadioGroup(labels=["BHA_1: BR0:1 TR0:-1 MotorYield:20", "BHA_2: BR0:1 TR0:-1 MotorYield:10", 'BHA_3: BR0:-1.5 TR0:-1 MotorYield:10',
                                         'BHA_4: BR0:1 TR0:-1 MotorYield:5', 'BHA_5: BR0:4 TR0:4 MotorYield:8'],active=0)   
    radio_group_BHA_1.on_change("active", on_radio_group_BHA_1_change) 
    
    
    full_data_1 = dict()

    # Define a button for json file uploading
    def on_button_upload_file_1_change(attr, old, new):
        for i in range(len(new['file_contents'])):
            # Store all uploaded data with files names
            full_data_1[new['file_name'][i]] = new['file_contents'][i]
                
        # View the first loaded file
        select_file_1.value = new['file_name'][0]
        select_file_1.options = list(full_data_1.keys())
        
    source_button_1 = ColumnDataSource({'file_contents': [], 'file_name': []})
    source_button_1.on_change('data', on_button_upload_file_1_change)

    button_upload_file_1 = Button(label="Upload Rectified Trajectory", button_type="primary", width=250)
    button_upload_file_1.callback = CustomJS(args=dict(file_source=source_button_1), code="""
    function error_handler(evt) {
        if(evt.target.error.name == "NotReadableError") {
            alert("Can't read file!");
        }
    }

    var input = document.createElement('input');
    input.setAttribute('type', 'file');
    input.setAttribute('multiple', true);
    input.accept = ".json"
    input.onchange = function(){
    
        if (window.FileReader) {
            // readAsDataURL represents the file's data as a base64 encoded string
            var names = []
            var contents = []
            var txt = new String(".txt")
            for (var i = 0; i < input.files.length; i++) {
                var f = input.files[i];            
                var reader = new FileReader();
                reader.onload = (function(f) {
                    return function(evt) {
                        var b64string = evt.target.result;
                        names.push(f.name);                       
                        contents.push(JSON.parse(b64string)); 
                        if (names.length == input.files.length) {
                            file_source.data = {'file_contents' : contents, 'file_name' : names};
                        }
                    };
                })(f);
                reader.onerror = error_handler;
                reader.readAsText(f);
            }
            //file_source.data = {'file_contents' : contents, 'file_name' : names};
        } else {
            alert('FileReader is not supported in this browser');
        }
    }
    input.click();
    """)

    # Define a button to upload original trajectory
    def on_button_upload_traj_plan_change(attr, old, new):
        # Store original traj 
        original_traj_data = dict()
        for i in range(len(new['file_contents'])):
            original_traj_data[new['file_name'][i]] = new['file_contents'][i]
        
        for k,v in original_traj_data.items():
            if k[-4:] == '.txt':
                content = v.split()
                i=2
                v_dic = {}
                v_dic['Stations'] = []
                while (5+i*6)<=len(content)-1:
                    temp = {}
                    for j in range(6):
                        temp[content[j]] = float(content[j+6*i])
                    v_dic['Stations'].append(temp)
                    i+=1
                original_traj_data = v_dic
                
        # When upload original traj, add it to the figure           
        for traj in original_traj_data['Stations']:
            traj['Incl'] = round(unit_util.degree_to_radian(traj['Incl']),2)
            traj['Azim'] = round(unit_util.degree_to_radian(traj['Azim']),2)
        
        if len(full_data_1) == 0:
            trajectories = []
        else:
            trajectories = full_data_1[select_file_1.value]
                 
        num = int(radio_group_BHA_1.active)
        BR0 = float(radio_group_BHA_1.labels[num].split()[1].split(':')[1])
        TR0 = float(radio_group_BHA_1.labels[num].split()[2].split(':')[1])
        MotorYield = float(radio_group_BHA_1.labels[num].split()[3].split(':')[1])
        BHA=(BR0,TR0,MotorYield)
        
        layout_control_1, layout_output_1 = refresh_page(trajectories, radio_group_1.active == 0, BHA, original_traj_data)
        update_layouts(layout_whole_1, generate_layouts_1(layout_control_1, layout_output_1))
        
        
    # define upload button                       
    source_button_original_traj = ColumnDataSource({'file_contents': [], 'file_name': []})
    source_button_original_traj.on_change('data', on_button_upload_traj_plan_change)
    
    button_upload_traj_plan = Button(label="Display Original Trajectory", button_type="primary", width=250)
    button_upload_traj_plan.callback = CustomJS(args=dict(file_source=source_button_original_traj), code="""
    function error_handler(evt) {
        if(evt.target.error.name == "NotReadableError") {
            alert("Can't read file!");
        }
    }

    var input = document.createElement('input');
    input.setAttribute('type', 'file');
    input.setAttribute('multiple', true);
    input.accept = ".json,.txt"
    input.onchange = function(){
    
        if (window.FileReader) {
            // readAsDataURL represents the file's data as a base64 encoded string
            var names = []
            var contents = []
            var txt = new String(".txt")
            for (var i = 0; i < input.files.length; i++) {
                var f = input.files[i];            
                var reader = new FileReader();
                reader.onload = (function(f) {
                    return function(evt) {
                        var b64string = evt.target.result;
                        names.push(f.name);
                        
                        if(f.name.slice(-4) == txt){
                            contents.push(b64string);  
                            //alert('txt input'); 
                                                
                        }else{
                            contents.push(JSON.parse(b64string));                                
                        };
                        
                        if (names.length == input.files.length) {
                            file_source.data = {'file_contents' : contents, 'file_name' : names};
                        }
                    };
                })(f);
                reader.onerror = error_handler;
                reader.readAsText(f);
            }
            //file_source.data = {'file_contents' : contents, 'file_name' : names};
        } else {
            alert('FileReader is not supported in this browser');
        }
    }
    input.click();
    """)

    
    
    # Arrange page layout
    #Page 1
    def generate_layouts(layout_control, layout_output):
        layout_select = column(widgetbox(button_upload_file), widgetbox(select_file), widgetbox(Div(text="""*Note: °/100ft""")),widgetbox(radio_group_BHA), layout_control, widgetbox(radio_group))
        layout_whole = row(layout_select, layout_output)
        return layout_whole
    
    #Page 2
    def generate_layouts_1(layout_control_1, layout_output_1):   
        layout_select_1 = column(widgetbox(button_upload_traj_plan),widgetbox(button_upload_file_1), widgetbox(select_file_1), widgetbox(Div(text="""*Note: °/100ft""")),widgetbox(radio_group_BHA_1), layout_control_1, widgetbox(radio_group_1))
        layout_whole_1 = row(layout_select_1, layout_output_1)  
        return layout_whole_1
       
    
    layout_control, layout_output = refresh_page([], radio_group.active == 0, [])
    layout_control_1, layout_output_1 = refresh_page([], radio_group_1.active == 0, [])
    
    layout_whole = generate_layouts(layout_control, layout_output)
    layout_whole_1 = generate_layouts_1(layout_control_1, layout_output_1)
    
    plan_page = Panel(child=layout_whole,title='Trajectory Plan')
    ops_page = Panel(child=layout_whole_1,title='Trajectory Ops Rectify')
    
    plan_ops_tab = Tabs(tabs=[plan_page,ops_page])
    
    def update_layouts(layout_whole,new_layout):
        layout_whole.children = new_layout.children
        
    def set_layouts(doc,layout_whole):
        doc.add_root(layout_whole)
        
    set_layouts(doc, plan_ops_tab)

io_loop = IOLoop.current()
show_page(curdoc())


if __name__ == '__main__':
    server = Server({'/': show_page}, num_procs=1)
    server.start()
    print('Opening Bokeh application on http://localhost:5006/')
    io_loop.add_callback(server.show, "/")
    io_loop.start()
