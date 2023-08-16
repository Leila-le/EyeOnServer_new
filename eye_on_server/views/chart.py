import pyecharts.options as opts
from pyecharts.charts import Line
from pyecharts.globals import CurrentConfig

from pyecharts.charts import Gauge

from pyecharts.charts import Pie

CurrentConfig.ONLINE_HOST = 'http://192.168.199.42:8000/static/js/echarts/'


class Chart(object):
    # 折线图
    def lines_chart(self, title, chart_id, x_data, y_data, y2_data):
        line_ = (
            Line()
            .set_global_opts(
                title_opts=opts.TitleOpts(title=title, pos_left='center', pos_top='20px'),
                tooltip_opts=opts.TooltipOpts(is_show=True, trigger='item', formatter="{}<br/>{b}"),
                xaxis_opts=opts.AxisOpts(type_="category"),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                    name='%',
                ),
            )
            .add_xaxis(xaxis_data=x_data)
            .add_yaxis(
                series_name="cpu使用率",
                y_axis=y_data,
                symbol="emptyCircle",
                is_symbol_show=True,
                label_opts=opts.LabelOpts(is_show=False),
                is_smooth=True
            )
            .add_yaxis(
                series_name="内存使用率",
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

    # 仪表盘
    def gauge_chart(self, title, chart_id, data):
        gauge_ = (
            Gauge()
            .add("", [("使用率", data)])
            .set_global_opts(title_opts=opts.TitleOpts(title=title))
        )
        gauge_.chart_id = chart_id
        return gauge_.render_embed()  # 返回框架,便于植入home.html中

    # 饼状图
    def pie_chart(self, title, chart_id, x_data, y_data):
        pie_ = (
            Pie()
            .add("", [list(z) for z in zip(x_data, y_data)])
            .set_colors(["blue", "green", "yellow", "red", "pink", "orange", "purple"])
            .set_global_opts(title_opts=opts.TitleOpts(title=title))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
            .render("pie_set_color.html")
        )
        pie_.chart_id = chart_id
        return pie_.render_embed()  # 返回框架,便于植入home.html中
