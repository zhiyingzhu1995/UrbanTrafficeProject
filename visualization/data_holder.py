import json
import pandas as pd
from visualization.data_filter import merge_yellow_taxi_data, filter_by_time, combine_zone_info

class DataSource:
    def __init__(self, path_dir = '../data'):
        self.path_dir = path_dir
        self.agg_column = ['trip_passenger', 'trip_speed_mph', 'trip_distance', 'total_price', 'price_per_mile']

        self.covid_19 = self.get_covid_19()
        self.covid_available_days = pd.Series(self.covid_19.index).dt.normalize().unique()

        self.zipcode_geo_json = self.get_zip_code_geo()
        self.taxi_geo_json = self.get_taxi_zone_geo()

        self.taxi_zone_df = self.get_taxi_zone()
        self.taxi_trip_df = self.get_yellow_taxi_data()
        self.zipcode_trip_df = self.get_yellow_taxi_by_zone()

        self.taxi_trip_filter_df = filter_by_time(self.taxi_trip_df,
                                                  year_range = [2019, 2020],
                                                  month_range = [3, 5], days_range = [1, 31],
                                                  hour_range = [0, 23],weekday_range = list(range(7)))

        self.taxi_merge_df = merge_yellow_taxi_data(self.taxi_trip_filter_df,self.taxi_zone_df, self.agg_column)
    def get_taxi_zone_geo(self):
        with open('%s/NYC Taxi Zones.geojson'%self.path_dir) as f:
            geo_json = json.load(f)
        return geo_json

    def get_zip_code_geo(self):
        with open('%s/nyc_zipcode.geojson'%self.path_dir) as f:
            geo_json = json.load(f)
        return geo_json

    def get_covid_19(self):
        covid_19 = pd.read_csv('%s/covid_info.csv'%self.path_dir, parse_dates=['time'])
        # covid_19['time'] = pd.to_datetime(dict(year=2020, month=covid_19.month, day=covid_19.day))
        # covid_19.drop(['month', 'day'], axis=1, inplace=True)
        covid_19.set_index('time', inplace=True)

        return covid_19

    def get_taxi_zone(self):
        taxi_zone_info = pd.read_csv('%s/taxi_zone_info_all.csv'%self.path_dir)
        taxi_zone_info.drop(columns=['centroid_x', 'centroid_y'], inplace=True)
        taxi_zone_info.rename(columns={"location_id": "zone"}, errors="raise", inplace=True)
        return taxi_zone_info

    def get_yellow_taxi_data(self):
        yellow_taxi_data = pd.read_csv('%s/yellow_taxi_all_clean.csv'%self.path_dir, parse_dates=['time'])
        yellow_taxi_data[['zone', 'num_pickup', 'num_dropoff', 'num_cash_payment', 'num_card_payment']] = yellow_taxi_data[
            ['zone', 'num_pickup', 'num_dropoff', 'num_cash_payment', 'num_card_payment']].astype('int32')

        # merge_df = pd.merge(yellow_taxi_data, self.taxi_zone_df, left_on='zone',
        #                     right_on='location_id')  # how='left' remove missing value - zone 264, 265
        # merge_df.drop(columns=['location_id', 'centroid_x', 'centroid_y'], inplace=True)
        # merge_df['weekday_name'] = merge_df['time'].dt.dayofweek

        # remove some error data
        yellow_taxi_data = yellow_taxi_data[yellow_taxi_data['avg_price_per_mile'] < 500]
        # merge_df = merge_df[merge_df['avg_trip_distance'] > 0.1]

        yellow_taxi_data.set_index('time', inplace=True)
        return yellow_taxi_data

    def get_yellow_taxi_by_zone(self):
        data = pd.merge(self.taxi_trip_df.reset_index(), self.taxi_zone_df[['zipcode','zone']],
                       left_on='zone',right_on='zone')
        # for name in self.agg_column:
        #     data['sum_%s'%name] = data['avg_%s'%name] * data['num_pickup']
        #     data.drop(columns=['avg_%s'%name], inplace=True)
        # group_df = data.groupby(['time','zipcode']).agg('sum').reset_index()
        #
        # for name in self.agg_column:
        #     group_df['avg_%s' % name] = group_df['sum_%s'%name] / group_df['num_pickup']
        #     group_df.drop(columns=['sum_%s'%name], inplace=True)

        group_df = combine_zone_info(data=data, agg_column=self.agg_column,
                                     group_by_criteria=['time','zipcode'])
        group_df.set_index('time', inplace=True)
        return group_df.drop(columns=['zone'])

# import json
# import pandas as pd
# from visualization.data_filter import filter_by_time, combine_zone_info
# from visualization.data_holder import DataSource
# self = DataSource('data')
