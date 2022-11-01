from os import pipe
import streamlit as st
import joblib
import pandas as pd
import matplotlib.pyplot as plt

best_model = joblib.load('xgboost.pkl')
pipeline = joblib.load('pipeline_model.pkl')
scorecard = joblib.load('scorecard.pkl')
complete_csv = pd.read_csv('preprocess_score.csv')

def main():
    st.title('Modelamiento de riesgo crediticio')
    st.sidebar.header('Caracteristicas del prestatario')

    def translate(feature:str, value:str):

        home_ownership = {
            'ALQUILER':'RENT',     'PROPIO':'OWN',
            'HIPOTECA':'MORTGAGE', 'OTROS':'OTHER'
        }

        verification_status = {
            'VERIFICADO': 'Verified',
            'FUENTE VERIFICADA': 'Source Verified',
            'NO VERIFICADO': 'Not Verified'
        }

        purpose = {
            'Tarjeta de credito':'credit_card', 'Carro': 'car',
            'Micro empresa': 'small_business', 'Boda':'wedding',
            'Consolidar deuda':'debt_consolidation', 'Mejora del hogar': 'home_improvement',
            'Compra importante': 'major_purchase', 'Salud': 'medical',
            'Traslado': 'moving', 'Vacaciones':'vacation',
            'Casa': 'house','Energia renovable': 'renewable_energy',
            'Educacion':'educational', 'Otros': 'other'
        }

        if feature == 'home_ownership':
            return home_ownership[value]
        elif feature == 'verification_status':
            return verification_status[value]
        elif feature == 'purpose':
            return purpose[value]
        else:
            return 'NO SE PAI'

    def user_input_parameters():
        term = st.sidebar.selectbox('Numero de pagos',(36,60))
        int_rate = st.sidebar.number_input('Tasa de interes', value=12.0)
        grade = st.sidebar.selectbox('Nota asignada por Lending club', ('A','B','C','D','E','F','G'))
        home_ownership = st.sidebar.selectbox('Estado de propiedad', ('ALQUILER','PROPIO','HIPOTECA','OTROS')) #TRADUCIR
        verification_status = st.sidebar.selectbox('Verificacion status', ('VERIFICADO','FUENTE VERIFICADA', 'NO VERIFICADO')) #TRADUCIR
        annual_inc = st.sidebar.number_input('Ingreso anual', value = 74000)
        purpose = st.sidebar.selectbox('Proposito del prestamo', ['Tarjeta de credito', 'Carro', 'Micro empresa', 'Boda',
                                                                'Consolidar deuda', 'Mejora del hogar', 'Compra importante',
                                                                'Salud', 'Traslado', 'Vacaciones', 'Casa', 'Energia renovable',
                                                                'Educacion', 'Otros']) #TRADUCIR
        dti = st.sidebar.number_input('DTI', value = 17.2)
        inq_last_6mths = st.sidebar.number_input('Numero de consultas en los ultimos 6 meses', value = 0)
        revol_util = st.sidebar.number_input('tasa de utilizacion de la linea rotatoria', value = 56.2)
        initial_list_status = st.sidebar.selectbox('Estado inicial de la lista del prestamo', ('f','w')) #QUESESO
        total_rec_int = st.sidebar.number_input('Intereses recibidos hasta la fecha', value = 2500.0)
        tot_cur_bal = st.sidebar.number_input('Saldo total de todas las cuentas', value = 130000.0)
        total_rev_hi_lim = st.sidebar.number_input('Limite del credito', value = 30000)
        mths_since_issue_d = st.sidebar.number_input('Meses desde que se hizo el prestamo', value = 83)
        mths_since_last_credit_pull_d = st.sidebar.number_input('Meses desde que saco credito para este prestamo', value = 60)

        try:
            home_ownership = translate('home_ownership', home_ownership)
            verification_status = translate('verification_status', verification_status)
            purpose = translate('purpose', purpose)
        except AssertionError as error:
            print(error)
            print('NO SE PUDO EJECUTAR TRANSLATE')

        data = {
            'term':term,
            'int_rate':int_rate,
            'grade': grade,
            'home_ownership': home_ownership,
            'annual_inc': annual_inc,
            'verification_status':verification_status,
            'purpose': purpose,
            'dti': dti,
            'inq_last_6mths': inq_last_6mths,
            'revol_util': revol_util,
            'initial_list_status': initial_list_status,
            'total_rec_int': total_rec_int,
            'tot_cur_bal': tot_cur_bal,
            'total_rev_hi_lim': total_rev_hi_lim,
            'mths_since_issue_d':mths_since_issue_d,
            'mths_since_last_credit_pull_d':mths_since_last_credit_pull_d,
        }

        features = pd.DataFrame(data, index =[0])
        return features
    data_0 = {
        'term':36,
        'int_rate': 100,
        'grade': 'A',
        'home_ownership': 'MORTAGE',
        'annual_inc': 77000,
        'verification_status':'Source Verified',
        'purpose': 'debt_consolidation',
        'dti': 21.91,
        'inq_last_6mths': 1,
        'revol_util': 53.5,
        'initial_list_status': 'f',
        'total_rec_int': 5000.06,
        'tot_cur_bal': 348253.0,
        'total_rev_hi_lim': 570000,
        'mths_since_issue_d':77.0,
        'mths_since_last_credit_pull_d':55.0,
    }
    df_0 = pd.DataFrame(data_0, index =[0])

    data_1 = {
        'term':36,
        'int_rate': 14.33,
        'grade': 'C',
        'home_ownership': 'MORTAGE',
        'annual_inc': 112000,
        'verification_status':'Not Verified',
        'purpose': 'debt_consolidation',
        'dti': 7.49,
        'inq_last_6mths': 2.0,
        'revol_util': 53.1,
        'initial_list_status': 'f',
        'total_rec_int': 2357.02,
        'tot_cur_bal': 0,
        'total_rev_hi_lim': 0,
        'mths_since_issue_d':96.0,
        'mths_since_last_credit_pull_d':61.0,
    }
    df_1 = pd.DataFrame(data_1, index =[0])

    st.markdown('En esta herramienta podrás predecir la probabilidad de que un individuo incumpla sus obligaciones financieras en los siguientes 12 meses a la fecha de originación un crédito adquirido. Para ello, debe diligenciar o modificar los datos que se encuentran a la izquierda según la necesidad y especificación del caso.')

    df = user_input_parameters()
    

    def classify(probabilitys,value, score=0):
        score = round(score)
        #return probabilitys
        if value[0] == 1:
            st.snow()
            return f'El prestatario va a incumplir con sus pagos con una probabilidad del {round(probabilitys[0][1]*100,2)} % y su Scorecard es de {score}.'
        else:
            st.balloons()
            return f'El prestatario va a cumplir con sus pagos con una probabilidad del {round(probabilitys[0][0]*100,2)} % y su Scorecard es de {score}.'

    def display_graph(df_score, percentile):
        fig,ax =  plt.subplots()
        ax.hist(complete_csv['score'], 100, )
        ax.axvline(df_score, color='r')  
        ax.legend([f'El scorecard del prestatario está por encima del {round(percentile,2)*100} % '])
        ax.set_xlabel('Scorecard')
        ax.set_ylabel('Cantidad de personas')
        st.pyplot(fig)  

    st.subheader('Ejemplo Caso 0')
    st.markdown('A continuacion se presenta un caso de ejemplo donde el prestatario va a **cumplir** con sus pagos.')
    st.dataframe(df_0)
    if st.button('EJECUTAR CASO 0'):
        new_df = pipeline.transform(df_0)
        df_score = scorecard.score(df_0)[0]
        st.success(classify(best_model.predict_proba(new_df), best_model.predict(new_df), df_score))
        percentile = len(complete_csv[complete_csv['score']<df_score])/complete_csv.shape[0]
        display_graph(df_score, percentile)
        
    
    st.subheader('Ejemplo Caso 1')
    st.markdown('A continuacion se presenta un caso de ejemplo donde el prestatario va a **incumplir** con sus pagos.')
    st.markdown('')
    st.dataframe(df_1)
    if st.button('EJECUTAR CASO 1'):
        new_df = pipeline.transform(df_1)
        df_score = scorecard.score(df_1)[0]
        st.success(classify(best_model.predict_proba(new_df), best_model.predict(new_df), df_score))
        percentile = len(complete_csv[complete_csv['score']<df_score])/complete_csv.shape[0]
        display_graph(df_score, percentile)
    
    st.subheader('Datos ingresados')
    st.dataframe(df)
    #new_df = pipe.transform(df)
    if st.button('EJECUTAR'):
        new_df = pipeline.transform(df)
        df_score = scorecard.score(df)[0]
        percentile = len(complete_csv[complete_csv['score']<df_score])/complete_csv.shape[0]
        st.success(classify(best_model.predict_proba(new_df), best_model.predict(new_df), df_score))
        display_graph(df_score, percentile)
        

if __name__ == '__main__':
    main()
