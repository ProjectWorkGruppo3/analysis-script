import boto3
import json

class TimestreamReader:
    def __init__(self):
        """Init with aws keys""" # FIXME
        session = boto3.Session()
        self.client = session.client('timestream-query')

    
    def get_timestream_data_in_csv(self):
        """Get Data From Timestream"""

        raw_rows, raw_columns = self.__request_data()

        rows = self.__get_data(raw_rows)
        columns = self.__get_columns(raw_columns)

        data_mapped_by_time = self.__get_data_mapped_by_time(rows, columns)
        
        data_with_json_property = self.__get_data_with_json_property(data_mapped_by_time)

        csv_columns, csv_data = self.__convert_to_csv_data_type(data_with_json_property)

        return csv_columns, csv_data


    def __request_data(self):
        """Request to timestream"""
        result = self.client.query(
            QueryString='SELECT * FROM "clod2021_ProjectWork_G3"."bracelet_data"'
        )

        raw_rows = result['Rows']
        raw_columns = result['ColumnInfo']

        return raw_rows, raw_columns

    def get_raw():
        """Get raw columns and rows"""

    def __get_columns(self, raw_columns):
        columns = []
        
        for c in raw_columns:
            columns.append(c['Name'])

        return columns

    def __get_data(self, raw_data):
        data = []

        for rd in raw_data:
            row = []
            for d in rd['Data']:
                row.append(list(d.values())[0])
            data.append(row)

        return data

    def __get_index_required(self, columns):
        
        time_index = columns.index('time')
        data_index = columns.index('measure_value::varchar')

        return time_index, data_index

    def __get_data_mapped_by_time(self, rows, columns):
        time_index, data_index = self.__get_index_required(columns)
        data = rows

        time_data = []
        for d in data:
            time = d[time_index]
            json_data = d[data_index]

            time_data.append({
                'time': time,
                'json': json_data
            })
        
        return time_data

    def __get_data_with_json_property(self, time_data):
        mapped = []

        for td in time_data:
            r = {
                'time': td['time']
            }
            dj = json.loads(td['json'])

            for k, v in dj.items():
                r[k] = v # uid or data
            
            mapped.append(r)
        
        return mapped

    def __convert_to_csv_data_type(self, data):
        csv = []
        csv_columns = ['time', 'uid']
        cc = []

        for d in data:
            csv_row = [d['time'], d['uid']]
            bracelet_data = d['data']
            keys = []

            for k, v in bracelet_data.items():
                csv_row.append(v)
                keys.append(k)
                
            cc = list(set(cc) | set(keys))

            
            csv.append(csv_row)

        # FIXME fix union, order of the columns its different respect of the data
        
        return csv_columns+cc, csv