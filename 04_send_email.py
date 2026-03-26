# %% [markdown]
# RETAIL MBR PIPELINE
# 
# Python Layer 4: Email Automation

# %%
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from email.mime.base      import MIMEBase
from email                import encoders
from pathlib              import Path
from datetime             import datetime
import pandas as pd

# %%
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH  = BASE_DIR / 'data' / 'warehouse' / 'master_kpi_trends.csv'
OUT_PATH   = BASE_DIR / 'output'

# %%
df           = pd.read_csv(DATA_PATH)
df['month']  = pd.to_datetime(df['month'])
latest_month = df['month'].max()
report_month = latest_month.strftime('%B %Y')
pdf_filename = f"MBR_Report_{latest_month.strftime('%Y_%m')}.pdf"
PDF_PATH     = OUT_PATH / pdf_filename

# %%
EMAIL_CONFIG = {
    'sender_email'    : 'vaibhav.shankdhar0602@gmail.com',  
    'sender_name'     : 'Vaibhav Shankdhar',
    'sender_password' : "ivbu yjcw zgfx acjx",  
    'recipient_list'  : [
        'shankdhar.vaibhav582@gmail.com',   
        'satanu03@gmail.com',                
    ],
    'smtp_server'     : 'smtp.gmail.com',
    'smtp_port'       : 587
}

# %%
def build_email_body(df, report_month):
    curr = df[df['month'] == df['month'].max()].agg({
        'revenue'           : 'sum',
        'ops'               : 'sum',
        'pcogs'             : 'sum',
        'profit_margin_pct' : 'mean',
        'conversion_rate'   : 'mean',
        'revenue_mom_pct'   : 'mean',
        'revenue_yoy_pct'   : 'mean',
        'margin_mom_change' : 'mean',
    })

    def arrow(val):
        if pd.isnull(val): return '→'
        return '▲' if val >= 0 else '▼'

    def color(val):
        if pd.isnull(val): return '#757575'
        return '#2E7D32' if val >= 0 else '#C62828'

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #212121;
                 max-width: 650px; margin: auto; padding: 20px;">

        <!-- Header -->
        <div style="background: #1565C0; padding: 30px;
                    border-radius: 8px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">
                📊 Monthly Business Review
            </h1>
            <p style="color: #BBDEFB; margin: 8px 0 0 0; font-size: 16px;">
                {report_month}
            </p>
        </div>

        <br/>

        <!-- Greeting -->
        <p style="font-size: 15px;">Hi Team,</p>
        <p style="font-size: 14px; color: #424242; line-height: 1.6;">
            Please find attached the <strong>Monthly Business Review
            for {report_month}</strong>. Below is a quick snapshot
            of our key performance indicators.
        </p>

        <!-- KPI Cards -->
        <table width="100%" cellpadding="0" cellspacing="10"
               style="margin: 20px 0;">
            <tr>
                <!-- Revenue -->
                <td width="33%" style="background: #F5F5F5;
                    border-radius: 8px; padding: 16px;
                    text-align: center; border-top: 4px solid #2196F3;">
                    <div style="font-size: 12px; color: #757575;
                                font-weight: bold;">REVENUE</div>
                    <div style="font-size: 22px; font-weight: bold;
                                color: #2196F3; margin: 6px 0;">
                        ${curr['revenue']:,.0f}
                    </div>
                    <div style="font-size: 11px;
                                color: {color(curr['revenue_mom_pct'])};">
                        {arrow(curr['revenue_mom_pct'])}
                        {abs(curr['revenue_mom_pct']):.1f}% MoM
                    </div>
                    <div style="font-size: 11px;
                                color: {color(curr['revenue_yoy_pct'])};">
                        {arrow(curr['revenue_yoy_pct'])}
                        {abs(curr['revenue_yoy_pct']):.1f}% YoY
                    </div>
                </td>

                <!-- OPS -->
                <td width="33%" style="background: #F5F5F5;
                    border-radius: 8px; padding: 16px;
                    text-align: center; border-top: 4px solid #4CAF50;">
                    <div style="font-size: 12px; color: #757575;
                                font-weight: bold;">OPS</div>
                    <div style="font-size: 22px; font-weight: bold;
                                color: #4CAF50; margin: 6px 0;">
                        ${curr['ops']:,.0f}
                    </div>
                    <div style="font-size: 11px; color: #757575;">
                        Ordered Product Sales
                    </div>
                </td>

                <!-- PCOGS -->
                <td width="33%" style="background: #F5F5F5;
                    border-radius: 8px; padding: 16px;
                    text-align: center; border-top: 4px solid #F44336;">
                    <div style="font-size: 12px; color: #757575;
                                font-weight: bold;">PCOGS</div>
                    <div style="font-size: 22px; font-weight: bold;
                                color: #F44336; margin: 6px 0;">
                        ${curr['pcogs']:,.0f}
                    </div>
                    <div style="font-size: 11px; color: #757575;">
                        Product Cost of Goods Sold
                    </div>
                </td>
            </tr>

            <tr>
                <!-- Profit Margin -->
                <td width="50%" style="background: #F5F5F5;
                    border-radius: 8px; padding: 16px;
                    text-align: center; border-top: 4px solid #FF9800;">
                    <div style="font-size: 12px; color: #757575;
                                font-weight: bold;">PROFIT MARGIN %</div>
                    <div style="font-size: 22px; font-weight: bold;
                                color: #FF9800; margin: 6px 0;">
                        {curr['profit_margin_pct']:.1f}%
                    </div>
                    <div style="font-size: 11px;
                                color: {color(curr['margin_mom_change'])};">
                        {arrow(curr['margin_mom_change'])}
                        {abs(curr['margin_mom_change']):.1f}pp MoM
                    </div>
                </td>

                <!-- Conversion Rate -->
                <td width="50%" style="background: #F5F5F5;
                    border-radius: 8px; padding: 16px;
                    text-align: center; border-top: 4px solid #9C27B0;">
                    <div style="font-size: 12px; color: #757575;
                                font-weight: bold;">CONVERSION RATE</div>
                    <div style="font-size: 22px; font-weight: bold;
                                color: #9C27B0; margin: 6px 0;">
                        {curr['conversion_rate']:.1f}%
                    </div>
                    <div style="font-size: 11px; color: #757575;">
                        Profitable Orders / Total Orders
                    </div>
                </td>
            </tr>
        </table>

        <!-- Divider -->
        <hr style="border: none; border-top: 1px solid #E0E0E0;
                   margin: 20px 0;"/>

        <!-- Footer note -->
        <p style="font-size: 13px; color: #424242; line-height: 1.6;">
            The full report with charts, regional breakdown, and
            6-month trend analysis is attached as a PDF.
        </p>
        <p style="font-size: 13px; color: #424242;">
            For any questions please reply to this email.
        </p>

        <br/>
        <p style="font-size: 13px;">
            Best regards,<br/>
            <strong>Vaibhav Shankdhar</strong><br/>
            <span style="color: #757575; font-size: 12px;">
                Senior Business Intelligence Engineer
            </span>
        </p>

        <!-- Auto-generated footer -->
        <div style="background: #F5F5F5; padding: 12px;
                    border-radius: 6px; margin-top: 20px;
                    text-align: center;">
            <p style="font-size: 10px; color: #9E9E9E; margin: 0;">
                This email was auto-generated by the Retail MBR Pipeline
                on {datetime.now().strftime('%d %B %Y at %H:%M')}.
                Do not reply directly to this automated message.
            </p>
        </div>

    </body>
    </html>
    """
    return html

# %%
def send_mbr_email():
    print(f"📧 Preparing MBR email for {report_month}...")

    # Validate PDF exists
    if not PDF_PATH.exists():
        print(f"❌ PDF not found: {PDF_PATH}")
        print("   Run 03_generate_pdf.py first!")
        return False

    # Build message
    msg = MIMEMultipart('alternative')
    msg['From']    = (f"{EMAIL_CONFIG['sender_name']} "
                      f"<{EMAIL_CONFIG['sender_email']}>")
    msg['To']      = ', '.join(EMAIL_CONFIG['recipient_list'])
    msg['Subject'] = (f"📊 Monthly Business Review — "
                      f"{report_month} | Retail MBR Pipeline")

    # Plain text fallback
    plain_text = (
        f"Hi Team,\n\n"
        f"Please find attached the MBR for {report_month}.\n\n"
        f"Revenue     : ${df[df['month']==df['month'].max()]['revenue'].sum():,.0f}\n"
        f"Profit Margin: {df[df['month']==df['month'].max()]['profit_margin_pct'].mean():.1f}%\n"
        f"Conv Rate   : {df[df['month']==df['month'].max()]['conversion_rate'].mean():.1f}%\n\n"
        f"Best regards,\nVaibhav Shankdhar"
    )
    msg.attach(MIMEText(plain_text, 'plain'))

    # HTML body
    html_body = build_email_body(df, report_month)
    msg.attach(MIMEText(html_body, 'html'))

    # Attach PDF
    with open(PDF_PATH, 'rb') as f:
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(f.read())
        encoders.encode_base64(attachment)
        attachment.add_header(
            'Content-Disposition',
            f'attachment; filename="{pdf_filename}"'
        )
        msg.attach(attachment)

    # Send via Gmail SMTP
    try:
        print(f"🔌 Connecting to Gmail SMTP...")
        server = smtplib.SMTP(
            EMAIL_CONFIG['smtp_server'],
            EMAIL_CONFIG['smtp_port']
        )
        server.starttls()
        server.login(
            EMAIL_CONFIG['sender_email'],
            EMAIL_CONFIG['sender_password']
        )

        for recipient in EMAIL_CONFIG['recipient_list']:
            server.sendmail(
                EMAIL_CONFIG['sender_email'],
                recipient,
                msg.as_string()
            )
            print(f"✅ Email sent to: {recipient}")

        server.quit()
        print(f"\n🎉 MBR email delivered successfully!")
        print(f"   Report: {pdf_filename}")
        print(f"   Month : {report_month}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed!")
        print("   Make sure you're using a Gmail App Password")
        print("   not your regular Gmail password.")
        return False

    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

# %% [markdown]
# You can't use your regular Gmail password. You need a special App Password:
# 
# * Go to myaccount.google.com
# * Click Security → 2-Step Verification → make sure it's ON
# * Go back to Security → search "App Passwords"
# * Click App Passwords
# * Select "Mail" and "Windows Computer"
# * Click Generate → copy the 16-character password
# * Paste it into EMAIL_CONFIG['sender_password']

# %%
if __name__ == '__main__':
    send_mbr_email()

# %%



