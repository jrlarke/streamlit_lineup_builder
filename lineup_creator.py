import streamlit as st
import pandas as pd
import itertools as it
import base64
from functools import reduce

class Combinations(object):
    """
    Creates different combinations using data in a dataframe
    """
    def __init__(self, dataframe, choice):
        self.dataframe = dataframe
        self.choice = choice
        self.group_size = choice['group_size']
        self.main_key = choice['main_key']
        self.keys = choice['keys']

    def _build_maps(self):
        out_dict = {}
        for key in self.keys:
            temp_dict = {}
            for index, row in enumerate(self.dataframe[self.main_key]):
                temp_dict.update({row: self.dataframe[key][index]})
            out_dict.update({key: temp_dict})
        return out_dict

    def combine(self):
        results = []
        data_maps = self._build_maps()
        for  item in it.combinations(self.dataframe[self.main_key], self.group_size):
            items = list(item)
            data_columns = [[] for l in  range(len(data_maps))]

            for x in item:
                for index, key in enumerate(self.keys):
                    data_columns[index].append(data_maps[key][x])

            for row in data_columns:
                items.extend(row)

            results.append(items)

        return pd.DataFrame(results)

class Formater(object):
    """
    Formats a dataFrame
    """
    def __init__(self, dataframe, choice, ufc):
        self.df = dataframe
        self.columns = choice['columns']
        self.extra_columns = choice['extra_columns']
        self.filters = choice['filters']
        self.ufc = ufc
        self._format_dataframe()
        self._apply_filters()
        if ufc is not None:
            self._apply_ufc()

    def _format_dataframe(self):
        self.df.rename(inplace=True, columns=self.columns)
        for column_name, column in self.extra_columns:
            df_column_names = [x for x in self.df.keys() if column in str(x)]
            self.df[column_name] = reduce(lambda x,y: x + self.df[y], df_column_names, 0)
        self.df.drop_duplicates(inplace=True)

    def _apply_filters(self):
        for column_name, value, operator in self.filters:
            if operator == 'le':
                temp = self.df[column_name] <= value
            elif operator  == 'lt':
                temp = self.df[column_name] < value
            elif operator  == 'ge':
                temp = self.df[column_name] >= value
            elif operator  == 'gt':
                temp = self.df[column_name] > value
            elif operator  == '==':
                temp = self.df[column_name] == value
            self.df = self.df[temp]

    def _apply_ufc(self):
        df = pd.DataFrame()
        for row in self.df.iterrows():
            temp_series = pd.Series(row[1])
            if len(set(temp_series.iloc[12:18].values)) == 6:
                temp_list = temp_series.iloc[18:24].tolist()
                count_1 = temp_list.count(self.ufc["group_num_1"])
                #count_2 = temp_list.count(self.ufc["group_num_2"])
                #count_3 = temp_list.count(self.ufc["group_num_3"])
                if (count_1 >= self.ufc["amount_num_1"]):
                    df = df.append(temp_series)
        if len(df) > 0:
            self.df = df[self.ufc['column_order']]
        else:
            print("RULES TOO RESTRICTIVE, no results, reverting dataframe")

    def get_dataframe(self):
        return self.df

MMA_DK = {
    "group_size" : 6,
    "main_key" : "Name + ID",
    "keys" : ["Salary", "Fight", "Group"],
    "columns": {6: '0 Salary', 7: '1 Salary', 8: '2 Salary',
                9: '3 Salary', 10: '4 Salary', 11: '5 Salary',
                12: '0 Fight', 13: '1 Fight', 14: '2 Fight',
                15: '3 Fight', 16: '4 Fight', 17: '5 Fight',
                18: '0 Group', 19: '1 Group', 20: '2 Group',
                21: '3 Group', 22: '4 Group', 23: '5 Group'
                },
    "extra_columns":[('DK Total Salary', 'Salary')],
    "filters":[('DK Total Salary', 50000, 'le'), ('DK Total Salary', 49500, 'ge')],
    "sort": 'DK Total Salary',
    "isUFC": True
    }

ufc_groups = {
    "group_num_1" : 1,
    "amount_num_1" : 1,
    #"group_num_2" : 2,
    #"amount_num_2" : 1,
    #"group_num_3" : 3,
    #"amount_num_3": 1,
    "column_order" : [0,1,2,3,4,5,
                '0 Salary','1 Salary','2 Salary','3 Salary','4 Salary','5 Salary', '0 Fight', '1 Fight',
                '2 Fight', '3 Fight', '4 Fight', '5 Fight',
                '0 Group','1 Group','2 Group','3 Group','4 Group','5 Group',
                'DK Total Salary']
}
def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

def run_creator_app():
    st.subheader('Choose a CSV to upload')
    st.write('For MMA required fields are: Name + ID, Salary, Fight, Group')

    uploaded_file = st.file_uploader("Choose a file", type=['csv'])

    if uploaded_file is not None:
        #st.write(type(uploaded_file))
        #file_details = {"filename":uploaded_file.name, "filetype":uploaded_file.type, "filesize":uploaded_file.size}
        #st.write(file_details)
        df = pd.read_csv(uploaded_file)
        ### would like to make this editable to allow user to change groups and rerun combinations ###
        ### st.dataframe(df)

        choice = MMA_DK
        my_combine = Combinations(df, choice)

        out = my_combine.combine()

        st.write("Came back with {} combinations".format(len(out)))
        out_filtered = out.head(100)

        if st.button("Download Data as CSV"):
            tmp_download_link = download_link(out_filtered, 'YOUR_DF.csv', 'Click here to download your data!')
            st.markdown(tmp_download_link, unsafe_allow_html=True)
        ufc = None
        returnedDf = None
        st.write("Filtering out invalid lineups")
        if 'isUFC' in choice and choice['isUFC']:
            if ufc is None:
                ufc = ufc_groups

        format_df = Formater(out.copy(deep=True), choice, ufc).get_dataframe()

        format_df.sort_values(by=choice['sort'], ascending=False, inplace=True)
        format_df = format_df.reset_index().drop('index', axis=1)
        st.write("Came back with {} valid lineups".format(len(format_df)))

        if st.button("Download Lineups as CSV"):
            tmp_download_link = download_link(format_df, 'lineups.csv', 'Click here to download your data!')
            st.markdown(tmp_download_link, unsafe_allow_html=True)
