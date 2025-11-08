import streamlit as st
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="แผนที่พยากรณ์อุบัติเหตุ", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    h1 {
        color: #d32f2f;
        text-align: center;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0px 24px;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚨 ระบบแสดงผลการพยากรณ์อุบัติเหตุบนท้องถนนในประเทศไทย")
st.title("ช่วงธันวาคม 2025 ถึง มกราคม 2026")

@st.cache_data
def load_data():
    """โหลดข้อมูลพยากรณ์และพิกัด"""
    try:
        # โหลดข้อมูลพยากรณ์
        forecast_df = pd.read_csv('forecast_2025_2026.csv')
        forecast_df['adate'] = pd.to_datetime(forecast_df['adate'])
        
        # โหลดข้อมูลพิกัด
        coord_df = pd.read_csv('coordinate/tambon.csv')
        
        # สร้าง mapping สำหรับอำเภอ
        coord_df['AM_ID_CLEAN'] = coord_df['AM_ID'].astype(str).str.zfill(4)
        
        # เลือกพิกัดที่ไม่ซ้ำกันสำหรับแต่ละอำเภอ (ใช้ค่าเฉลี่ย)
        amphoe_coord = coord_df.groupby(['AM_ID_CLEAN', 'AMPHOE_T', 'CHANGWAT_T']).agg({
            'LAT': 'mean',
            'LONG': 'mean',
            'CH_ID': 'first'
        }).reset_index()
        
        return forecast_df, amphoe_coord
    except Exception as e:
        st.error(f"ไม่สามารถโหลดข้อมูลได้: {str(e)}")
        return None, None

# โหลดข้อมูล
forecast_df, amphoe_coord = load_data()

if forecast_df is not None and amphoe_coord is not None:
    
    # Sidebar Filters
    st.sidebar.header("🔍 ตัวกรอง")
    
    # ช่วงวันที่
    min_date = forecast_df['adate'].min().date()
    max_date = forecast_df['adate'].max().date()
    
    st.sidebar.subheader("📅 ช่วงเวลา")
    
    col_date1, col_date2 = st.sidebar.columns(2)
    
    with col_date1:
        start_date = st.date_input(
            "วันที่เริ่มต้น",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
            key="start_date_input"
        )
    
    with col_date2:
        end_date = st.date_input(
            "วันที่สิ้นสุด",
            value=max_date,
            min_value=start_date,  # ให้วันสิ้นสุดเริ่มต้นที่วันเริ่มต้นเป็นอย่างต่ำ
            max_value=max_date,
            key="end_date_input"
        )
    
    # กรองตามวันที่
    filtered_df = forecast_df[
        (forecast_df['adate'].dt.date >= start_date) & 
        (forecast_df['adate'].dt.date <= end_date)
    ].copy()
    
    # เตรียมข้อมูลสำหรับตัวกรอง
    filtered_df['rcode_str'] = filtered_df['rcode'].astype(str).str.zfill(4)
    
    # รวมข้อมูล
    merged_df = filtered_df.merge(
        amphoe_coord,
        left_on='rcode_str',
        right_on='AM_ID_CLEAN',
        how='left'
    )
    
    # จังหวัด filter
    st.sidebar.subheader("🏙️ จังหวัด")
    provinces = sorted(merged_df['CHANGWAT_T'].dropna().unique().tolist())
    provinces.insert(0, "ทั้งหมด")
    selected_province = st.sidebar.selectbox("เลือกจังหวัด", provinces, key="province_select")
    
    # กรองข้อมูลตามจังหวัดที่เลือก
    if selected_province != "ทั้งหมด":
        merged_df = merged_df[merged_df['CHANGWAT_T'] == selected_province]
    
    # อำเภอ filter - แสดงเฉพาะอำเภอในจังหวัดที่เลือก
    st.sidebar.subheader("🏘️ อำเภอ")
    amphoes = sorted(merged_df['AMPHOE_T'].dropna().unique().tolist())
    amphoes.insert(0, "ทั้งหมด")
    selected_amphoe = st.sidebar.selectbox("เลือกอำเภอ", amphoes, key="amphoe_select")
    
    if selected_amphoe != "ทั้งหมด":
        merged_df = merged_df[merged_df['AMPHOE_T'] == selected_amphoe]
        # อัพเดทจังหวัดให้ตรงกับอำเภอที่เลือก (ในกรณีที่เลือก "ทั้งหมด" ที่จังหวัด)
        if selected_province == "ทั้งหมด":
            selected_province = merged_df['CHANGWAT_T'].iloc[0] if len(merged_df) > 0 else "ทั้งหมด"
            st.sidebar.info(f"ℹ️ จังหวัด: {selected_province}")
    
    # รวมจำนวนอุบัติเหตุตามอำเภอ
    with st.spinner('กำลังประมวลผลข้อมูล...'):
        accident_summary = merged_df.groupby(
            ['AM_ID_CLEAN', 'AMPHOE_T', 'CHANGWAT_T', 'LAT', 'LONG']
        )['predicted_cases'].sum().reset_index()
    
    # สร้าง Tabs
    tab1, tab2, tab3 = st.tabs(["🗺️ แผนที่", "📊 การวิเคราะห์", "📋 ตารางข้อมูล"])
    
    # Tab 1: แผนที่
    with tab1:
        # ข้อมูลเพิ่มเติม - ย้ายมาไว้บน
        with st.expander("ℹ️ คำอธิบาย", expanded=False):
            st.markdown("""
            ### วิธีใช้งาน
            - **ช่วงเวลา**: เลือกช่วงวันที่ที่ต้องการดูข้อมูล (วันสิ้นสุดจะปรับตามวันเริ่มต้นอัตโนมัติ)
            - **จังหวัด/อำเภอ**: กรองข้อมูลตามพื้นที่ที่สนใจ (เมื่อเลือกอำเภอ จังหวัดจะแสดงอัตโนมัติ)
            - **แผนที่**: 
                - จุดสีแดงแสดงตำแหน่งอุบัติเหตุ พร้อมเอฟเฟกต์กะพริบแบบภัยพิบัติ
                - **ขนาดของวงกลม**: ปรับตามสัดส่วนจำนวนอุบัติเหตุในข้อมูลที่แสดง (ใหญ่ = มาก, เล็ก = น้อย)
                - **สีของวงกลม**: แบ่งเป็น 5 ระดับตามจำนวนอุบัติเหตุ (เหลือง → ส้ม → แดง)
                - **วางเมาส์เหนือจุด** เพื่อดูชื่อพื้นที่และจำนวนอุบัติเหตุ
                - **คลิกที่จุด** เพื่อดูข้อมูลละเอียดเพิ่มเติม
                - แผนที่ความร้อน (HeatMap) แสดงความหนาแน่นของอุบัติเหตุ
            
            ### การคำนวณขนาดวงกลม
            - ระบบใช้ **Min-Max Normalization** เพื่อปรับขนาดให้สัมพันธ์กับข้อมูลที่แสดง
            - สูตร: `ขนาด = 8 + ((ค่าปัจจุบัน - ค่าต่ำสุด) / (ค่าสูงสุด - ค่าต่ำสุด)) × 17`
            - ขนาดอยู่ระหว่าง 8-25 พิกเซล เพื่อความชัดเจนและไม่ทับซ้อน
            
            ### สีบนแผนที่
            - 🟡 **เหลือง**: จำนวนอุบัติเหตุต่ำ
            - 🟠 **ส้ม**: จำนวนอุบัติเหตุปานกลาง
            - 🔴 **แดง**: จำนวนอุบัติเหตุสูง
            """)
        
        # กำหนดศูนย์กลางและ zoom ของแผนที่ให้พอดีกับประเทศไทย
        if len(accident_summary) > 0:
            # คำนวณขอบเขตของข้อมูล
            valid_coords = accident_summary[accident_summary['LAT'].notna() & accident_summary['LONG'].notna()]
            
            if len(valid_coords) > 0:
                min_lat, max_lat = valid_coords['LAT'].min(), valid_coords['LAT'].max()
                min_lon, max_lon = valid_coords['LONG'].min(), valid_coords['LONG'].max()
                center_lat = (min_lat + max_lat) / 2
                center_lon = (min_lon + max_lon) / 2
                
                # คำนวณ zoom level ที่เหมาะสม
                lat_diff = max_lat - min_lat
                lon_diff = max_lon - min_lon
                max_diff = max(lat_diff, lon_diff)
                
                if max_diff > 10:
                    zoom_start = 6
                elif max_diff > 5:
                    zoom_start = 7
                elif max_diff > 2:
                    zoom_start = 8
                elif max_diff > 1:
                    zoom_start = 9
                else:
                    zoom_start = 10
            else:
                center_lat, center_lon = 13.736717, 100.523186
                zoom_start = 6
        else:
            # ค่า default สำหรับประเทศไทย
            center_lat, center_lon = 13.736717, 100.523186
            zoom_start = 6
        
        # สร้างแผนที่
        with st.spinner('กำลังสร้างแผนที่...'):
            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=zoom_start,
                tiles='CartoDB dark_matter'
            )
        
        # เตรียมข้อมูลสำหรับ HeatMap with Time
        if len(accident_summary) > 0:
            # คำนวณขนาดวงกลมแบบ normalized - ใช้ค่า min/max จากข้อมูลทั้งหมดในตอนนั้น
            max_cases = accident_summary['predicted_cases'].max()
            min_cases = accident_summary['predicted_cases'].min()
            
            # สร้างสีตาม quantile - แก้ไขเพื่อป้องกัน error
            try:
                # ใช้ qcut ถ้าข้อมูลมีความหลากหลายเพียงพอ
                unique_values = accident_summary['predicted_cases'].nunique()
                if unique_values >= 5:
                    accident_summary['color_intensity'] = pd.qcut(
                        accident_summary['predicted_cases'], 
                        q=5, 
                        labels=['#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#bd0026'],
                        duplicates='drop'
                    )
                else:
                    # ใช้ cut แทนถ้าข้อมูลไม่หลากหลาย
                    accident_summary['color_intensity'] = pd.cut(
                        accident_summary['predicted_cases'], 
                        bins=5, 
                        labels=['#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#bd0026'],
                        duplicates='drop',
                        include_lowest=True
                    )
            except Exception:
                # ถ้ายังมีปัญหา ใช้การแบ่งแบบง่าย
                def get_color(value):
                    if max_cases == min_cases:
                        return '#fd8d3c'
                    ratio = (value - min_cases) / (max_cases - min_cases)
                    if ratio <= 0.2:
                        return '#ffffb2'
                    elif ratio <= 0.4:
                        return '#fecc5c'
                    elif ratio <= 0.6:
                        return '#fd8d3c'
                    elif ratio <= 0.8:
                        return '#f03b20'
                    else:
                        return '#bd0026'
                
                accident_summary['color_intensity'] = accident_summary['predicted_cases'].apply(get_color)
            
            # เพิ่มจุดบนแผนที่พร้อมเอฟเฟกต์กะพริบ
            heat_data = []
            
            # เพิ่ม progress bar สำหรับการเพิ่มจุด
            progress_bar = st.progress(0)
            total_points = len(accident_summary)
            
            for idx, row in accident_summary.iterrows():
                if pd.notna(row['LAT']) and pd.notna(row['LONG']):
                    # คำนวณขนาดจุดแบบ normalized ตามสัดส่วนของข้อมูลทั้งหมด
                    # ใช้ min-max normalization เพื่อให้ขนาดสม่ำเสมอ
                    if max_cases > min_cases:
                        # Normalize ค่าให้อยู่ระหว่าง 0-1
                        normalized_value = (row['predicted_cases'] - min_cases) / (max_cases - min_cases)
                        # ปรับขนาดให้อยู่ในช่วง 8-25 พิกเซล
                        radius = 8 + (normalized_value * 17)
                    else:
                        # ถ้าค่าเท่ากันหมด ใช้ขนาดกลาง
                        radius = 15
                    
                    # สร้าง popup ที่มีข้อมูลละเอียด
                    info_html = f"""
                    <div style='font-family: "Sarabun", Arial; min-width: 250px; padding: 10px;'>
                        <h3 style='color: #d32f2f; margin: 0 0 10px 0; border-bottom: 2px solid #d32f2f; padding-bottom: 5px;'>
                            📍 {row['AMPHOE_T']}
                        </h3>
                        <p style='margin: 8px 0; font-size: 14px;'><b>🏙️ จังหวัด:</b> {row['CHANGWAT_T']}</p>
                        <p style='margin: 8px 0; font-size: 14px;'><b>🚨 จำนวนอุบัติเหตุพยากรณ์:</b> 
                            <span style='color: #d32f2f; font-size: 18px; font-weight: bold;'>{row['predicted_cases']:.0f}</span> ครั้ง
                        </p>
                        <p style='margin: 8px 0; font-size: 12px; color: #666;'>
                            <b>📌 พิกัด:</b> {row['LAT']:.4f}, {row['LONG']:.4f}
                        </p>
                        <hr style='margin: 10px 0; border: none; border-top: 1px solid #ddd;'>
                        <p style='margin: 5px 0; font-size: 11px; color: #999; text-align: center;'>
                            คลิกที่จุดอื่นเพื่อดูข้อมูลเพิ่มเติม
                        </p>
                    </div>
                    """
                    
                    # สร้าง tooltip แบบสั้นสำหรับ hover
                    tooltip_text = f"🏘️ {row['AMPHOE_T']}: {row['predicted_cases']:.0f} ครั้ง"
                    
                    # เพิ่ม CircleMarker พร้อม tooltip และ popup
                    folium.CircleMarker(
                        location=[row['LAT'], row['LONG']],
                        radius=radius,
                        popup=folium.Popup(info_html, max_width=300),
                        tooltip=tooltip_text,
                        color='red',
                        fillColor=row['color_intensity'],
                        fillOpacity=0.7,
                        weight=2,
                        className='pulse-marker'
                    ).add_to(m)
                    
                    # เพิ่มข้อมูลสำหรับ HeatMap
                    heat_data.append([row['LAT'], row['LONG'], row['predicted_cases']])
                
                # Update progress bar
                progress_bar.progress((idx + 1) / total_points)
            
            # ลบ progress bar เมื่อเสร็จ
            progress_bar.empty()
            
            # เพิ่ม HeatMap layer
            if heat_data:
                from folium.plugins import HeatMap
                HeatMap(
                    heat_data,
                    min_opacity=0.2,
                    max_opacity=0.8,
                    radius=25,
                    blur=35,
                    gradient={
                        0.0: 'blue',
                        0.3: 'lime',
                        0.5: 'yellow',
                        0.7: 'orange',
                        1.0: 'red'
                    }
                ).add_to(m)
        
        # เพิ่ม CSS สำหรับเอฟเฟกต์กะพริบ (ไม่ขยับตำแหน่ง)
        pulse_css = """
        <style>
        @keyframes pulse {
            0% {
                opacity: 1;
                filter: brightness(1);
            }
            50% {
                opacity: 0.3;
                filter: brightness(1.5);
            }
            100% {
                opacity: 1;
                filter: brightness(1);
            }
        }
        
        .pulse-marker {
            animation: pulse 2s ease-in-out infinite;
        }
        
        /* สุ่มความเร็วการกะพริบแบบภัยพิบัติ */
        .leaflet-interactive:nth-child(5n) {
            animation-duration: 1.2s;
            animation-delay: 0.1s;
        }
        
        .leaflet-interactive:nth-child(5n+1) {
            animation-duration: 2.5s;
            animation-delay: 0.4s;
        }
        
        .leaflet-interactive:nth-child(5n+2) {
            animation-duration: 1.7s;
            animation-delay: 0.7s;
        }
        
        .leaflet-interactive:nth-child(5n+3) {
            animation-duration: 2.1s;
            animation-delay: 0.3s;
        }
        
        .leaflet-interactive:nth-child(5n+4) {
            animation-duration: 1.9s;
            animation-delay: 0.6s;
        }
        </style>
        """
        
        m.get_root().html.add_child(folium.Element(pulse_css))
        
        # เพิ่ม fullscreen option
        plugins.Fullscreen().add_to(m)
        
        # แสดงแผนที่
        st_folium(m, width=None, height=600, key="main_map", returned_objects=[])
    
    # Tab 2: การวิเคราะห์
    with tab2:
        # แสดงสถิติภาพรวม
        st.subheader("📊 สถิติภาพรวม")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📍 จำนวนอุบัติเหตุทั้งหมด", f"{accident_summary['predicted_cases'].sum():.0f}")
        
        with col2:
            st.metric("🏘️ จำนวนอำเภอ", len(accident_summary))
        
        with col3:
            if len(accident_summary) > 0:
                top_amphoe = accident_summary.loc[accident_summary['predicted_cases'].idxmax(), 'AMPHOE_T']
                st.metric("🔝 อำเภอที่มีอุบัติเหตุสูงสุด", top_amphoe)
            else:
                st.metric("🔝 อำเภอที่มีอุบัติเหตุสูงสุด", "N/A")
        
        with col4:
            st.metric("📈 ค่าเฉลี่ยต่อวัน", f"{merged_df.groupby('adate')['predicted_cases'].sum().mean():.1f}")
        
        st.markdown("---")
        
        # กราฟวิเคราะห์
        st.subheader("📈 กราฟวิเคราะห์")
        
        # สร้าง 2 columns สำหรับกราฟ
        col_graph1, col_graph2 = st.columns(2)
        
        with col_graph1:
            st.markdown("##### 📅 แนวโน้มอุบัติเหตุตามวันที่")
            # กราฟแนวโน้มตามวันที่
            daily_trend = merged_df.groupby('adate')['predicted_cases'].sum().reset_index()
            daily_trend['adate'] = pd.to_datetime(daily_trend['adate'])
            
            fig_trend = px.line(
                daily_trend, 
                x='adate', 
                y='predicted_cases',
                labels={'adate': 'วันที่', 'predicted_cases': 'จำนวนอุบัติเหตุ'},
                template='plotly_white'
            )
            fig_trend.update_traces(line_color='#d32f2f', line_width=3)
            fig_trend.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=20, b=20),
                hovermode='x unified'
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col_graph2:
            st.markdown("##### 🏆 Top 10 อำเภอที่มีอุบัติเหตุสูงสุด")
            # Top 10 อำเภอ
            top_amphoes = accident_summary.nlargest(10, 'predicted_cases')
            top_amphoes['label'] = top_amphoes['AMPHOE_T'] + ', ' + top_amphoes['CHANGWAT_T']
            
            fig_top = px.bar(
                top_amphoes,
                x='predicted_cases',
                y='label',
                orientation='h',
                labels={'predicted_cases': 'จำนวนอุบัติเหตุ', 'label': 'อำเภอ'},
                template='plotly_white',
                color='predicted_cases',
                color_continuous_scale=['#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#bd0026']
            )
            fig_top.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=20, b=20),
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'}
            )
            fig_top.update_coloraxes(showscale=False)
            st.plotly_chart(fig_top, use_container_width=True)
        
        # กราฟเพิ่มเติมแถวที่ 2
        col_graph3, col_graph4 = st.columns(2)
        
        with col_graph3:
            st.markdown("##### 📆 การกระจายอุบัติเหตุตามวันในสัปดาห์")
            # วิเคราะห์ตามวันในสัปดาห์
            filtered_df_copy = merged_df.copy()
            filtered_df_copy['day_of_week_num'] = filtered_df_copy['adate'].dt.dayofweek
            filtered_df_copy['day_of_week_thai'] = filtered_df_copy['day_of_week_num'].map({
                0: 'จันทร์', 1: 'อังคาร', 2: 'พุธ', 3: 'พฤหัสบดี',
                4: 'ศุกร์', 5: 'เสาร์', 6: 'อาทิตย์'
            })
            
            day_trend = filtered_df_copy.groupby(['day_of_week_num', 'day_of_week_thai'])['predicted_cases'].sum().reset_index()
            day_trend = day_trend.sort_values('day_of_week_num')
            
            fig_day = px.bar(
                day_trend,
                x='day_of_week_thai',
                y='predicted_cases',
                labels={'day_of_week_thai': 'วัน', 'predicted_cases': 'จำนวนอุบัติเหตุ'},
                template='plotly_white',
                color='predicted_cases',
                color_continuous_scale='Reds'
            )
            fig_day.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=20, b=20),
                showlegend=False
            )
            fig_day.update_coloraxes(showscale=False)
            st.plotly_chart(fig_day, use_container_width=True)
        
        with col_graph4:
            st.markdown("##### 🗺️ การกระจายอุบัติเหตุตามจังหวัด (Top 10)")
            # Top 10 จังหวัด
            province_summary = merged_df.groupby('CHANGWAT_T')['predicted_cases'].sum().reset_index()
            province_summary = province_summary.nlargest(10, 'predicted_cases')
            
            fig_province = px.pie(
                province_summary,
                values='predicted_cases',
                names='CHANGWAT_T',
                template='plotly_white',
                color_discrete_sequence=px.colors.sequential.Reds_r
            )
            fig_province.update_traces(textposition='inside', textinfo='percent+label')
            fig_province.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=20, b=20),
                showlegend=False
            )
            st.plotly_chart(fig_province, use_container_width=True)
        
        # สถิติเชิงลึก
        st.markdown("---")
        st.subheader("📉 สถิติเชิงลึก")
        
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        
        with stat_col1:
            median_cases = accident_summary['predicted_cases'].median()
            st.metric("📊 ค่ามัธยฐาน", f"{median_cases:.1f}")
        
        with stat_col2:
            std_cases = accident_summary['predicted_cases'].std()
            st.metric("📐 ส่วนเบี่ยงเบนมาตรฐาน", f"{std_cases:.1f}")
        
        with stat_col3:
            total_days = filtered_df['adate'].nunique()
            st.metric("📅 จำนวนวันทั้งหมด", f"{total_days}")
        
        with stat_col4:
            avg_per_day = filtered_df.groupby('adate')['predicted_cases'].sum().mean()
            st.metric("📈 เฉลี่ยต่อวัน", f"{avg_per_day:.1f}")
    
    # Tab 3: ตารางข้อมูล
    with tab3:
        st.subheader("📋 ตารางข้อมูลรายละเอียด")
        
        display_df = accident_summary[['CHANGWAT_T', 'AMPHOE_T', 'predicted_cases']].copy()
        display_df.columns = ['จังหวัด', 'อำเภอ', 'จำนวนอุบัติเหตุ (ครั้ง)']
        display_df = display_df.sort_values('จำนวนอุบัติเหตุ (ครั้ง)', ascending=False)
        display_df['จำนวนอุบัติเหตุ (ครั้ง)'] = display_df['จำนวนอุบัติเหตุ (ครั้ง)'].apply(lambda x: f"{x:.0f}")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
        
        # ส่วนดาวน์โหลดข้อมูล
        st.markdown("---")
        st.subheader("💾 ดาวน์โหลดข้อมูล")
        
        download_col1, download_col2 = st.columns(2)
        
        with download_col1:
            # ดาวน์โหลดข้อมูลสรุป
            csv_summary = accident_summary[['CHANGWAT_T', 'AMPHOE_T', 'predicted_cases', 'LAT', 'LONG']].copy()
            csv_summary.columns = ['จังหวัด', 'อำเภอ', 'จำนวนอุบัติเหตุ', 'ละติจูด', 'ลองจิจูด']
            
            st.download_button(
                label="📥 ดาวน์โหลดข้อมูลสรุป (CSV)",
                data=csv_summary.to_csv(index=False, encoding='utf-8-sig'),
                file_name=f"accident_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with download_col2:
            # ดาวน์โหลดข้อมูลแนวโน้มรายวัน
            daily_trend_download = filtered_df.groupby('adate')['predicted_cases'].sum().reset_index()
            daily_trend_download['adate'] = daily_trend_download['adate'].dt.strftime('%Y-%m-%d')
            daily_trend_download.columns = ['วันที่', 'จำนวนอุบัติเหตุ']
            
            st.download_button(
                label="📥 ดาวน์โหลดข้อมูลรายวัน (CSV)",
                data=daily_trend_download.to_csv(index=False, encoding='utf-8-sig'),
                file_name=f"accident_daily_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

else:
    st.error("⚠️ ไม่สามารถโหลดข้อมูลได้ กรุณาตรวจสอบไฟล์ข้อมูล")
