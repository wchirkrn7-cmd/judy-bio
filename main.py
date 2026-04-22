import discord
from discord.ext import commands
from discord import app_commands
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import threading
import asyncio

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def run_automation(search_value, search_type, result_container):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 40)
    
    try:
        driver.get("https://logbook.tpmap.in.th/")
        
        user_field = wait.until(EC.element_to_be_clickable((By.NAME, "username")))
        user_field.send_keys("pelcd801218")
        pass_field = driver.find_element(By.NAME, "password")
        pass_field.send_keys("45762819")
        pass_field.send_keys(Keys.ENTER)
        
        time.sleep(8)
        driver.get("https://logbook.tpmap.in.th/table")
        
        member_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'สมาชิกในครัวเรือน')]")))
        driver.execute_script("arguments[0].click();", member_tab)
        time.sleep(5)

        if search_type == "name":
            radio_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='radio' and contains(@value, 'name')]")))
        elif search_type == "cid":
            radio_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='radio' and @value='by_nid']")))
        elif search_type == "surname":
            radio_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='radio' and @value='by_surname']")))
            
        driver.execute_script("arguments[0].click();", radio_btn)
        time.sleep(2)

        input_target = wait.until(EC.presence_of_element_located((By.ID, "input_findpeople")))
        driver.execute_script("arguments[0].value = arguments[1];", input_target, search_value)
        input_target.send_keys(Keys.SPACE + Keys.BACKSPACE) 

        search_btn = wait.until(EC.element_to_be_clickable((By.ID, "btn_findpeople")))
        driver.execute_script("arguments[0].click();", search_btn)
        
        time.sleep(15)

        rows = driver.find_elements(By.XPATH, "//table//tr[td]")
        if len(rows) > 0:
            all_data = [r.text for r in rows if r.text.strip()]
            result_container['data'] = "\n---\n".join(all_data)
        else:
            result_container['data'] = "ไม่พบข้อมูลในระบบ"

    except Exception as e:
        result_container['data'] = f"System Error: {str(e)}"
    finally:
        driver.quit()

class SurnameModal(discord.ui.Modal, title='กรอกนามสกุลเพื่อค้นหา'):
    last_name = discord.ui.TextInput(
        label='นามสกุล (Surname)',
        placeholder='กรอกนามสกุลที่นี่...',
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🔍 กำลังดึงข้อมูลจากนามสกุล: **{self.last_name.value}**", ephemeral=True)
        
        res_data = {'data': None}
        surname = self.last_name.value
        thread = threading.Thread(target=run_automation, args=(surname, "surname", res_data))
        thread.start()

        while thread.is_alive():
            await asyncio.sleep(2)

        output = res_data['data'] or "ไม่พบข้อมูล"
        if len(output) > 1000:
            with open("Judyพ่อพวกมึง.txt", "w", encoding="utf-8") as f:
                f.write(output)
            await interaction.followup.send("✅ ข้อมูลยาวเกินไป ส่งเป็นไฟล์แทน", file=discord.File("Judyพ่อพวกมึง.txt"), ephemeral=True)
            os.remove("Judyพ่อพวกมึง.txt")
        else:
            final_embed = discord.Embed(title="📊 ผลการค้นหา (นามสกุล)", color=discord.Color.orange())
            final_embed.add_field(name="นามสกุล", value=surname, inline=False)
            final_embed.add_field(name="Data Extract", value=f"```\n{output}\n```", inline=False)
            await interaction.followup.send(embed=final_embed, ephemeral=True)

class CIDModal(discord.ui.Modal, title='กรอกเลขบัตรประชาชน'):
    cid_input = discord.ui.TextInput(label='เลขบัตรประชาชน (CID)', min_length=13, max_length=13, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🔍 กำลังค้นหา CID: **{self.cid_input.value}**", ephemeral=True)
        res_data = {'data': None}
        cid = self.cid_input.value
        thread = threading.Thread(target=run_automation, args=(cid, "cid", res_data))
        thread.start()
        while thread.is_alive():
            await asyncio.sleep(2)
        output = res_data['data'] or "ไม่พบข้อมูล"
        if len(output) > 1000:
            with open("Judyพ่อพวกมึง.txt", "w", encoding="utf-8") as f: f.write(output)
            await interaction.followup.send("✅ ข้อมูลยาวเกินไป ส่งเป็นไฟล์แทน", file=discord.File("Judyพ่อพวกมึง.txt"), ephemeral=True)
            os.remove("Judyพ่อพวกมึง.txt")
        else:
            final_embed = discord.Embed(title="📊 ผลการค้นหา (CID)", color=discord.Color.purple())
            final_embed.add_field(name="CID", value=cid, inline=False)
            final_embed.add_field(name="Data Extract", value=f"```\n{output}\n```", inline=False)
            await interaction.followup.send(embed=final_embed, ephemeral=True)

class SearchModal(discord.ui.Modal, title='กรอกข้อมูลเพื่อค้นหา'):
    first_name = discord.ui.TextInput(label='ชื่อ (First Name)', placeholder='กรอกชื่อ...', required=True)
    last_name = discord.ui.TextInput(label='นามสกุล (Last Name)', placeholder='กรอกนามสกุล...', required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f" กำลังค้นหาชื่อ: **{self.first_name.value} {self.last_name.value}**", ephemeral=True)
        res_data = {'data': None}
        full_name = f"{self.first_name.value} {self.last_name.value}"
        thread = threading.Thread(target=run_automation, args=(full_name, "name", res_data))
        thread.start()
        while thread.is_alive():
            await asyncio.sleep(2)
        output = res_data['data'] or "ไม่พบข้อมูล"
        if len(output) > 1000:
            with open("Judyพ่อพวกมึง.txt", "w", encoding="utf-8") as f: f.write(output)
            await interaction.followup.send("✅ ข้อมูลยาวเกินไป ส่งเป็นไฟล์แทน", file=discord.File("Judyพ่อพวกมึง.txt"), ephemeral=True)
            os.remove("Judyพ่อพวกมึง.txt")
        else:
            final_embed = discord.Embed(title=" ผลการค้นหา (ชื่อ-นามสกุล)", color=discord.Color.green())
            final_embed.add_field(name="ชื่อ-นามสกุล", value=full_name, inline=False)
            final_embed.add_field(name="ข้อมูลทั้งหมด", value=f"```\n{output}\n```", inline=False)
            await interaction.followup.send(embed=final_embed, ephemeral=True)

class MainMenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label=" ค้นหาด้วยชื่อ", style=discord.ButtonStyle.success, custom_id="search_name_btn")
    async def search_name_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SearchModal())

    @discord.ui.button(label=" ค้นหาด้วย CID", style=discord.ButtonStyle.success, custom_id="search_cid_btn")
    async def search_cid_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CIDModal())

    @discord.ui.button(label=" ค้นหานามสกุล", style=discord.ButtonStyle.success, custom_id="search_surname_btn")
    async def search_surname_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SurnameModal())

@bot.command()
async def menu(ctx):
    embed = discord.Embed(
        title="Judy 1881",
        description="ระบบดึงข้อมูลอัตโนมัติ\nเลือกโหมดที่ต้องการด้านล่าง:",
        color=discord.Color.blue()
    )

    embed.set_image(url="https://img2.pic.in.th/1000033487.webp") 
    await ctx.send(embed=embed, view=MainMenuView())

@bot.event
async def on_ready():
    print(f'Judy: Online as {bot.user}')

bot.run(os.getenv("TOKEN"))
