from pyecharts.charts import Line
from pyecharts import options as opts
from pyecharts.charts import Timeline
# CurrentConfig.ONLINE_HOST = 'http://192.168.199.42:8000/static/js/echarts/'
# CurrentConfig.ONLINE_HOST = 'http://127.0.0.1:8000/static/js/echarts/'


class Chart(object):
    # 折线图
    def lines_chart(self, title, chart_id, x_data, y_data, y2_data, disk):
        t1 = Timeline()
        line_ = (
            Line(opts.InitOpts(width='100%', height='100%'))
            .set_global_opts(
                title_opts=opts.TitleOpts(title=title, pos_left='center', pos_top='20px'),
                tooltip_opts=opts.TooltipOpts(is_show=True, trigger='axis'),
                legend_opts=opts.LegendOpts(pos_left='left', border_width=0),
                xaxis_opts=opts.AxisOpts(type_="category"),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                    name='%',
                ),
                datazoom_opts=[
                    opts.DataZoomOpts(range_start=0, range_end=100),  # 设置底部缩放条
                    opts.DataZoomOpts(type_="inside", range_start=0, range_end=100),  # 设置图内滚轮可缩放
                ],
            )
            .add_xaxis(xaxis_data=x_data)
            .add_yaxis(
                series_name="CPU",
                y_axis=y_data,
                symbol="emptyCircle",
                is_symbol_show=True,
                label_opts=opts.LabelOpts(is_show=False),
                is_smooth=True
            )
            .add_yaxis(
                series_name="内存",
                y_axis=y2_data,
                symbol="emptyCircle",
                is_symbol_show=True,
                label_opts=opts.LabelOpts(is_show=False),
                is_smooth=True
            )
            # .render("Basic_line_chart.html")
        )
        line_.chart_id = chart_id
        return line_.render_embed()  # 返回框架,便于植入home.html中


