from selenium import webdriver
from re import search
import time
import xlsxwriter
from math import factorial

supers = []


def valid_domain(string):
    return string in supers


def valid_subdomain(subs, string, base, deity_subs):
    string = string.split(" (")
    end = ""
    try:
        end = string[1].split(")")[0]
    except:
        end = ""
    if (end != "" and end != base):
        return False

    for sub_fam in deity_subs:
        if string[0] in sub_fam:
            return False
    return string[0] in subs


def combinations(n, r):
    return (factorial(n))/(factorial(r) * factorial(n - r))


# Create an Excel Sheet
workbook = xlsxwriter.Workbook('deities.xlsx')
worksheet = workbook.add_worksheet()
worksheet.write("A1", "Deity")
worksheet.write("B1", "Domains")
worksheet.write("C1", "Subdomains")
worksheet.write("D1", "Combinations")

driver = webdriver.Firefox()

driver.get("https://www.d20pfsrd.com/classes/core-classes/cleric/domains")
time.sleep(2)

total = driver.find_elements_by_xpath(
    "/html/body/div[1]/div[4]/div/div/main/section/article/div[2]/div[1]/div[1]/div/div[5]/div[1]/div/ul")

total = total[0].text.split("\n")

domains = []
placeholder = []
last = ""
for domain in total:
    if "Domain" in domain:
        domains.append((last, placeholder))
        last = domain.split(" ")[0]
        placeholder = []
    else:
        placeholder.append(domain)

clean_domains = []
[clean_domains.append((x)) for x in domains if x not in clean_domains]
domains = clean_domains
supers = [x[0] for x in domains]

driver.get("https://aonprd.com/DeitiesByGroup.aspx")

deities = driver.find_elements_by_xpath("//table/tbody/tr/td[1]")
deities = [x.text for x in deities]

offset = 2

total_combinations = 0
for i in range(len(deities)):
    print(f"{i/len(deities) * 100}%  - {i}/{len(deities)}")
    deity = deities[i]
    driver.get(f"https://aonprd.com/DeityDisplay.aspx?ItemName={deity}")
    worksheet.write(f"A{i+offset}", deity)

    deity_side = driver.find_elements_by_xpath("//table/tbody/tr/td/span/b")
    deity_side = [x.text for x in deity_side]

    if "Domains" in deity_side:
        idx = deity_side.index("Domains")
        deity_elems = driver.find_elements_by_xpath(
            f"//table/tbody/tr/td/span/a")
        deity_dmns = [x.text for x in deity_elems if valid_domain(x.text)]
        deity_subs = []
        dmn_string = ""
        for domain in deity_dmns:
            (name, subs) = domains[supers.index(domain)]
            dmn_string += name + ", "
            deity_subs.append([
                x.text.split(" ")[0] for x in deity_elems if valid_subdomain(subs, x.text, name, deity_subs)])

        sub_string = ""
        sub_counts = [1 + len(x) for x in deity_subs]
        for subs in deity_subs:
            for sub in subs:
                sub_string += sub + ", "

        worksheet.write(f"B{i+offset}", dmn_string)
        worksheet.write(f"C{i+offset}", sub_string)

        count = 0
        for x in sub_counts:
            count += x

        num_combinations = combinations(count, 2)
        for x in sub_counts:
            if (x > 1):
                num_combinations -= combinations(x, 2)

        worksheet.write(f"D{i+offset}", num_combinations)
        total_combinations += num_combinations
        print(f"Total combinations currently: {total_combinations}")

    else:
        next

worksheet.write("F4", "Total Combinations Possible")
worksheet.write("F5", total_combinations)

workbook.close()
driver.close()
