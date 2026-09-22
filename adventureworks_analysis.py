import matplotlib.pyplot as plt
import pandas as pd
import pyodbc
import seaborn as sns

# Bağlantı Ayarları
SERVER = "localhost"
DATABASE = "AdventureWorks2025"
DRIVER = "{ODBC Driver 17 for SQL Server}"


def get_db_connection():
  """Veritabanı bağlantısını açar."""
  conn_str = f"DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};Trusted_connection=yes;"
  return pyodbc.connect(conn_str)


def fetch_rfm_data():
  """SSMS'te oluşturduğumuz View üzerinden detaylı RFM verilerini çeker."""
  conn = get_db_connection()
  # Hem segmenti hem de harcama (Monetary) verisini alıyoruz
  query = """
    SELECT Segment, CustomerID, Monetary 
    FROM vw_CustomerRFMSegments
    """
  df = pd.read_sql(query, conn)
  conn.close()
  return df


def plot_customer_counts(df):
  """1. Grafik: Segmentlere Göre Müşteri Sayısı"""
  # Segment bazlı müşteri sayılarını hesaplayalım
  df_counts = (
      df.groupby("Segment")["CustomerID"].count().reset_index(name="MusteriSayisi")
  )

  plt.figure(figsize=(12, 6))
  sns.set_theme(style="whitegrid")
  ax = sns.barplot(
      x="Segment",
      y="MusteriSayisi",
      data=df_counts,
      palette="crest",
      hue="Segment",
      legend=False,
  )

  plt.title(
      "AdventureWorks - Müşteri Segment Dağılımı",
      fontsize=16,
      fontweight="bold",
      pad=15,
  )
  plt.xlabel("Müşteri Segmenti", fontsize=12, fontweight="bold")
  plt.ylabel("Müşteri Sayısı", fontsize=12, fontweight="bold")
  plt.xticks(rotation=30, fontsize=10)

  # Sütunların üzerine müşteri sayılarını yazdıralım
  for p in ax.patches:
    ax.annotate(
        f"{int(p.get_height())}",
        (p.get_x() + p.get_width() / 2.0, p.get_height()),
        ha="center",
        va="center",
        xytext=(0, 8),
        textcoords="offset points",
        fontsize=10,
        fontweight="bold",
    )

  plt.tight_layout()
  plt.show()


def plot_segment_revenue(df):
  """2. Grafik: Segmentlere Göre Toplam Ciro (Monetary)"""
  # Segment bazlı toplam ciroyu hesaplayalım
  df_revenue = (
      df.groupby("Segment")["Monetary"].sum().reset_index(name="ToplamCiro")
  )

  plt.figure(figsize=(12, 6))
  sns.set_theme(style="whitegrid")
  ax = sns.barplot(
      x="Segment",
      y="ToplamCiro",
      data=df_revenue,
      palette="magma",
      hue="Segment",
      legend=False,
  )

  plt.title(
      "AdventureWorks - Segment Bazlı Toplam Ciro",
      fontsize=16,
      fontweight="bold",
      pad=15,
  )
  plt.xlabel("Müşteri Segmenti", fontsize=12, fontweight="bold")
  plt.ylabel("Toplam Ciro ($)", fontsize=12, fontweight="bold")
  plt.xticks(rotation=30, fontsize=10)

  # Barların üzerine ciro değerlerini binlik formatta yazdıralım
  for p in ax.patches:
    height = p.get_height()
    ax.annotate(
        f"${height:,.0f}",
        (p.get_x() + p.get_width() / 2.0, height),
        ha="center",
        va="center",
        xytext=(0, 8),
        textcoords="offset points",
        fontsize=10,
        fontweight="bold",
    )

  plt.tight_layout()
  plt.show()


if __name__ == "__main__":
  print("Veriler SSMS'teki View üzerinden çekiliyor...")
  df_rfm = fetch_rfm_data()

  print("1. Grafik (Müşteri Dağılımı) oluşturuluyor...")
  plot_customer_counts(df_rfm)

  print("2. Grafik (Segment Ciroları) oluşturuluyor...")
  plot_segment_revenue(df_rfm)