import pyecharts.options as opts
from pyecharts.charts import Line
from pyecharts.globals import CurrentConfig


CurrentConfig.ONLINE_HOST = 'http://192.168.199.42:8000/static/js/echarts/'


class Chart(object):
    # 折线图
    def line_chart(self, title, chart_id, x_data, y_data):
        line_ = (
            Line()
            .set_global_opts(
                title_opts=opts.TitleOpts(title=title, pos_left='center', pos_top='20px'),
                tooltip_opts=opts.TooltipOpts(is_show=False),
                xaxis_opts=opts.AxisOpts(type_="category"),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
            )
            .add_xaxis(xaxis_data=x_data)
            .add_yaxis(
                series_name="",
                y_axis=y_data,
                symbol="emptyCircle",
                is_symbol_show=True,
                label_opts=opts.LabelOpts(is_show=False),
            )

            # .render("basic_line_chart.html")
        )
        line_.chart_id = chart_id
        line_.render_embed()  # 返回框架,便于植入home.html中
