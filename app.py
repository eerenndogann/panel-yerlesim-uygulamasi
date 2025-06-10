import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import base64
import io
from fpdf import FPDF
import tempfile

# Sayfa ayarı
st.set_page_config(page_title="Panel ve Alan Yerleşim Hesaplayıcı", layout="centered")

# Görseli base64'e çevirme
def image_to_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Logoları yükle
logo1_b64 = image_to_base64("logo_beyaz_nobg.png")
logo2_b64 = image_to_base64("SPUTEK_isim.png")

# Logo ve başlık
st.markdown(
    f"""
    <div style="display: flex; justify-content: center; margin-bottom: 20px;">
        <div style="
            background-color: rgba(255, 255, 255, 0.05);
            padding: 20px 40px;
            border-radius: 20px;
            display: flex;
            flex-direction: row;
            align-items: center;
            gap: 10px;
            box-shadow: 0 0 8px 1px #00ffcc, 0 0 12px 1px #00ffcc;">
            <img src="data:image/png;base64,{logo1_b64}" width="100"/>
            <img src="data:image/png;base64,{logo2_b64}" width="200"/>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---", unsafe_allow_html=True)
st.markdown(
    """
    <p style="text-align: center; font-size: 24px; color: gray;">
        Sputek Teknoloji A.Ş. – Mobil & Akıllı GES Uygulamaları
    </p>
    """,
    unsafe_allow_html=True
)

# Panel tipleri
panel_tipleri = {
    "Tip A – 166mm x 83mm – 3.159 Wp": (0.166, 0.083, 3.159),
    "Tip B – 91mm x 182mm – 4.5 Wp": (0.091, 0.182, 4.5),
    "Tip C – 105mm x 182.2mm – 5.2 Wp": (0.105, 0.1822, 5.2),
    "Tip D – 79.375mm x 158.75mm – 2.8 Wp": (0.079375, 0.15875, 2.8)
}

kenar_bosluk = 0.03
hucre_bosluk = 0.003

st.subheader(" Hücre Grubu Oluştur")
tip_secimi = st.selectbox("🔧 Hücre Tipi", list(panel_tipleri.keys()))
hucre_en, hucre_boy, hucre_guc = panel_tipleri[tip_secimi]
satir = st.number_input("🔢 Matris Satır (Y)", min_value=1, value=6)
sutun = st.number_input("🔢 Matris Sütun (X)", min_value=1, value=12)

panel_genislik = sutun * hucre_en + (sutun - 1) * hucre_bosluk
panel_yukseklik = satir * hucre_boy + (satir - 1) * hucre_bosluk
cati_en = panel_genislik + 2 * kenar_bosluk
cati_boy = panel_yukseklik + 2 * kenar_bosluk

toplam_hucre = satir * sutun
panel_grubu_gucu_wp = toplam_hucre * hucre_guc
panel_grubu_gucu_kwp = panel_grubu_gucu_wp / 1000

st.success(f"📐 Hücre Grubu Boyutu (kenarlı çerçeve ile):")
st.markdown(f"- Genişlik: **{cati_en:.3f} m**")
st.markdown(f"- Yükseklik: **{cati_boy:.3f} m**")

st.success(f"🔋 Toplam Güç (1 Hücre Grubu): {toplam_hucre} hücre × {hucre_guc:.3f} Wp = **{panel_grubu_gucu_wp:.1f} Wp** ({panel_grubu_gucu_kwp:.2f} kWp)")

# Görsel çizim 1
fig1, ax1 = plt.subplots()
ax1.set_xlim(0, cati_en)
ax1.set_ylim(0, cati_boy)
ax1.set_aspect('equal')
ax1.set_title("Hücre Grubu Yerleşimi")
ax1.add_patch(patches.Rectangle((0, 0), cati_en, cati_boy, linewidth=1.5, edgecolor='black', facecolor='lightgrey'))

start_x = kenar_bosluk
start_y = kenar_bosluk
for i in range(int(sutun)):
    for j in range(int(satir)):
        x = start_x + i * (hucre_en + hucre_bosluk)
        y = start_y + j * (hucre_boy + hucre_bosluk)
        ax1.add_patch(patches.Rectangle((x, y), hucre_en, hucre_boy, linewidth=0.4, edgecolor='gray', facecolor='aqua'))

st.pyplot(fig1)

# Alan yerleşimi
st.subheader("Alan Yerleşimi Hesapla (boşluksuz)")
verilen_genislik = st.number_input("📏 Alan Genişliği (m)", min_value=0.1, value=5.0)
verilen_yukseklik = st.number_input("📏 Alan Yüksekliği (m)", min_value=0.1, value=5.0)
yerlesim_yonu = st.radio("📐 Yerleşim Yönü", ["Yatay", "Dikey"])

if yerlesim_yonu == "Yatay":
    grup_en = cati_en
    grup_boy = cati_boy
else:
    grup_en = cati_boy
    grup_boy = cati_en

adet_x = int(verilen_genislik // grup_en)
adet_y = int(verilen_yukseklik // grup_boy)
toplam_grup = adet_x * adet_y
sistem_toplam_guc_wp = toplam_grup * panel_grubu_gucu_wp
sistem_toplam_guc_kwp = sistem_toplam_guc_wp / 1000

st.success(f"🧮 Bu alana {adet_x} x {adet_y} = **{toplam_grup} adet panel grubu** sığar.")

# Görsel çizim 2
fig2, ax2 = plt.subplots()
ax2.set_xlim(0, verilen_genislik)
ax2.set_ylim(0, verilen_yukseklik)
ax2.set_aspect('equal')
ax2.set_title(" Alana Panel Grubu Yerleşimi (boşluksuz)")

for i in range(adet_x):
    for j in range(adet_y):
        x = i * grup_en
        y = j * grup_boy
        ax2.add_patch(patches.Rectangle((x, y), grup_en, grup_boy, linewidth=0.8, edgecolor='black', facecolor='aqua', alpha=0.6))

st.pyplot(fig2)

# Güç özeti
st.markdown("---")
st.markdown(
    f"""
    <div style="text-align: center; font-size: 18px; color: gray;">
        📊 <strong>Sistem Güç Özeti</strong><br>
        ▪ Bir panel grubunun gücü: <strong>{panel_grubu_gucu_wp:.1f} Wp</strong><br>
        ▪ Alana yerleşen panel grubu sayısı: <strong>{toplam_grup} adet</strong><br>
        ▪ Toplam sistem gücü: <strong style="color: #00ffcc;">{sistem_toplam_guc_wp:.1f} Wp</strong> 
        (<strong>{sistem_toplam_guc_kwp:.2f} kWp</strong>)
    </div>
    """,
    unsafe_allow_html=True
)

# PDF için figürleri geçici dosyaya kaydet
with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp1:
    fig1.savefig(tmp1.name, format="png")
    fig1_path = tmp1.name

with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp2:
    fig2.savefig(tmp2.name, format="png")
    fig2_path = tmp2.name

# PDF oluştur
pdf = FPDF()
pdf.add_page()
pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
pdf.set_font('DejaVu', '', 14)
pdf.cell(200, 10, txt="Panel ve Alan Yerleşim Raporu", ln=True, align="C")
pdf.ln(10)
pdf.set_font('DejaVu', '', 10)
pdf.multi_cell(0, 10, txt=f"""
Seçilen Hücre Tipi: {tip_secimi}
Matris: {satir} x {sutun}
Hücre Grubu Boyutu: {cati_en:.3f} m x {cati_boy:.3f} m
Toplam Hücre: {toplam_hucre}
Panel Grubu Gücü: {panel_grubu_gucu_wp:.1f} Wp ({panel_grubu_gucu_kwp:.2f} kWp)

Alan: {verilen_genislik} m x {verilen_yukseklik} m
Yerleşim Yönü: {yerlesim_yonu}
Yerleşen Grup: {adet_x} x {adet_y} = {toplam_grup}
Toplam Sistem Gücü: {sistem_toplam_guc_wp:.1f} Wp ({sistem_toplam_guc_kwp:.2f} kWp)
""")
pdf.image(fig1_path, x=10, w=180)
pdf.add_page()
pdf.image(fig2_path, x=10, w=180)

# PDF çıktısını base64 ile indirilebilir hale getir
pdf_bytes = pdf.output(dest='S').encode('latin1')
pdf_output = io.BytesIO(pdf_bytes)
b64_pdf = base64.b64encode(pdf_output.read()).decode('utf-8')
href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="yerlesim_raporu.pdf">📄 PDF olarak indir</a>'
st.markdown(href, unsafe_allow_html=True)

# Alt Bilgi
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; font-size: 16px; color: gray;">
        🔋 Geliştirici: <strong>Sputek Teknoloji A.Ş.</strong> – Mobil & Akıllı GES Uygulamaları |
        <span style="font-weight: bold;">Eren Doğan</span>
    </div>
    """,
    unsafe_allow_html=True
)
