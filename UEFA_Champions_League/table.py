import scrapy

def fifth(lst):
    start = 0
    end = 5

    while start < len(lst):
        yield lst[start:end]

        start +=5
        end +=5


class TableSpider(scrapy.Spider):
    name = "table"
    start_urls = ["https://www.espn.com/football/table/_/league/UEFA.CHAMPIONS/season/2021"]

    def parse(self, response):
        dt = {}

        teams_rows = response.css("table")[0].css("tr")
        details_rows = response.css("table")[1].css("tr")

        for group, group_details in zip(fifth(teams_rows), fifth(details_rows)):
            group_label = group[0].css("td span::text").get()

            dt[group_label] = {}

            for team, detail in zip(group[1:],group_details[1:]):
                teams_label = team.css("td span.hide-mobile a::text").get()
                table_detail = detail.css("td span::text").getall()

                dt[group_label][teams_label] = {
                    "wins": table_detail[1],
                    "draws": table_detail[2],
                    "loses": table_detail[3],
                    "points": table_detail[-1]


                }

        yield dt
