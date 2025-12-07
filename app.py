import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='KGS Lead Estimator', layout='wide')
st.title('KGS Lead Estimator')

# ====== Global Controls ======
st.markdown('### Global Settings')
conv_percent = st.number_input(
    'Conversion Rate (%)', min_value=0.0, max_value=100.0, value=30.0, step=1.0,
    help='Enter the expected percentage of leads that convert to deals.'
)
conversion_rate = conv_percent / 100.0

# ====== Hardcoded options ======
lead_types = ['end-user', 'distributor', 'installer', 'consultant']
countries = ['BE','NL','UK','IE','FR','IT','ES','PT','DE','DK','SE','FI','NO','PL','TR','ZA','ME']
industries = [
    'hospitality','datacenters','factories','gas & oil','healthcare','education','retail','transportation',
    'manufacturing','energy','government','banking','insurance','telecommunications','construction','real estate',
    'food & beverage','pharmaceutical','mining','utilities','logistics','media','sports','entertainment','other'
]
technologies = [
    'high-end addressable system',
    'mid-end addressable',
    'conventional','wireless','aspirating smoke detection','linear heat detection','flame detection','evacuation'
]

# ====== Estimation parameters ======
tech_base_values = {
    'high-end addressable system': 35000,
    'mid-end addressable': 15000,
    'aspirating smoke detection': 14000,
    'evacuation': 13000,
    'wireless': 9000,
    'conventional': 7000,
    'linear heat detection': 6000,
    'flame detection': 5000
}

lead_type_multiplier = {'end-user':1.2,'distributor':1.5,'installer':1.1,'consultant':1.3}
country_multiplier = {'BE':1.0,'NL':1.0,'UK':1.1,'IE':1.0,'FR':1.0,'IT':1.0,'ES':1.0,'PT':1.0,'DE':1.1,'DK':1.0,'SE':1.0,'FI':1.0,'NO':1.0,'PL':0.9,'TR':0.8,'ZA':0.9,'ME':1.2}
industry_multiplier = {
    'hospitality':1.1,'datacenters':1.4,'factories':1.3,'gas & oil':1.5,'healthcare':1.3,'education':1.2,'retail':1.1,
    'transportation':1.2,'manufacturing':1.3,'energy':1.4,'government':1.2,'banking':1.3,'insurance':1.2,
    'telecommunications':1.3,'construction':1.2,'real estate':1.1,'food & beverage':1.2,'pharmaceutical':1.4,
    'mining':1.5,'utilities':1.3,'logistics':1.2,'media':1.1,'sports':1.1,'entertainment':1.1,'other':1.0
}

# ====== Session state ======
if 'persons' not in st.session_state:
    st.session_state['persons'] = [{
        'lead_type': lead_types[0],
        'country': countries[0],
        'industry': industries[0],
        'technology': technologies[0],
        'count': 1
    }]

st.markdown('---')
st.markdown('### Leads Input')

def person_form(index):
    st.subheader(f'Lead {index+1}')
    cols = st.columns([1,1,1,1,1])
    lead_type = cols[0].selectbox('Lead Type', lead_types, key=f'lead_type_{index}', index=lead_types.index(st.session_state['persons'][index]['lead_type']))
    country = cols[1].selectbox('Country', countries, key=f'country_{index}', index=countries.index(st.session_state['persons'][index]['country']))
    industry = cols[2].selectbox('Industry', industries, key=f'industry_{index}', index=industries.index(st.session_state['persons'][index]['industry']))
    technology = cols[3].selectbox('Technology Interest', technologies, key=f'tech_{index}', index=technologies.index(st.session_state['persons'][index]['technology']))
    count = cols[4].number_input('Number Count', min_value=1, step=1, value=st.session_state['persons'][index]['count'], key=f'count_{index}')
    return {'lead_type':lead_type,'country':country,'industry':industry,'technology':technology,'count':int(count)}

for i in range(len(st.session_state['persons'])):
    st.session_state['persons'][i] = person_form(i)

if st.button('Add Lead'):
    st.session_state['persons'].append({
        'lead_type': lead_types[0],
        'country': countries[0],
        'industry': industries[0],
        'technology': technologies[0],
        'count': 1
    })

if st.button('Start Estimation'):
    if len(st.session_state['persons']) == 0:
        st.warning('Please add at least one lead.')
    else:
        with st.spinner('Estimating...'):
            estimates_raw = []
            estimates_effective = []
            for person in st.session_state['persons']:
                base = tech_base_values.get(person['technology'], 5000)
                value = base
                value *= lead_type_multiplier.get(person['lead_type'], 1)
                value *= country_multiplier.get(person['country'], 1)
                value *= industry_multiplier.get(person['industry'], 1)
                estimates_raw.append(value)
                effective_value = value * person['count'] * conversion_rate
                estimates_effective.append(effective_value)

            total_estimate = sum(estimates_effective)
            low = total_estimate * 0.8
            high = total_estimate * 1.2

            st.subheader('Estimation Results')
            c1, c2, c3 = st.columns(3)
            c1.metric('Low Estimate', f"€{low:,.2f}")
            c2.metric('Expected Estimate', f"€{total_estimate:,.2f}")
            c3.metric('High Estimate', f"€{high:,.2f}")

            df = pd.DataFrame(st.session_state['persons'])
            df['EstimateRaw'] = estimates_raw
            df['Estimate'] = estimates_effective

            st.markdown('### Visualizations')
            tech_group = df.groupby('technology')['Estimate'].sum().reset_index()
            fig_tech = px.bar(tech_group, x='technology', y='Estimate', color='technology', title='Lead Value by Technology Interest')
            st.plotly_chart(fig_tech, use_container_width=True)

            industry_group = df.groupby('industry')['Estimate'].sum().reset_index()
            fig_industry = px.bar(industry_group, x='industry', y='Estimate', color='industry', title='Lead Value by Industry')
            st.plotly_chart(fig_industry, use_container_width=True)

            country_group = df.groupby('country')['Estimate'].sum().reset_index()
            fig_country = px.bar(country_group, x='country', y='Estimate', color='country', title='Lead Value by Country')
            st.plotly_chart(fig_country, use_container_width=True)
