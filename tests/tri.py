"""Vérifie les décisions dans Chromium avec deux bibliothèques privées."""
import json
import os
import secrets
import shutil
from playwright.sync_api import sync_playwright, expect
from parcours import BASE, ROOT, occ, dav, password

members = []


def login(browser, uid):
    context = browser.new_context(viewport={"width": 390, "height": 844})
    page = context.new_page()
    page.goto(BASE + "/login")
    page.locator("input[name=user]").fill(uid)
    page.locator("input[type=password]").fill(password)
    page.locator("input[type=password]").press("Enter")
    page.wait_for_url("**/apps/**")
    page.goto(BASE + "/apps/familytri/")
    expect(page.locator("#family-review")).to_be_visible()
    return page


def test_review():
    for _ in range(2):
        uid = "tri-" + secrets.token_hex(6)
        occ("user:add", "--password-from-env", uid, create=True)
        members.append(uid)
    owner, other = members
    base = f"/remote.php/dav/files/{owner}/"
    for name, fixture in [("prise.jpg", "mire.jpg"), ("seconde.jpg", "mire-floue.jpg"),
                          ("prise-copie.jpg", "mire.jpg")]:
        dav(owner, "PUT", base + name, [201], (ROOT / "tests" / fixture).read_bytes())
    occ("memories:index", "--user", owner)
    job = json.loads(occ("background-job:list", "-c", r"OCA\FamilyTri\BackgroundJob\Analyse", "--output=json"))[0]
    occ("background-job:execute", job["id"], "--force-execute")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get("CHROME_BIN") or shutil.which("chromium") or shutil.which("google-chrome"))
        page = login(browser, owner)
        section = page.locator(".serie").filter(has_text="prise.jpg")
        expect(section).to_have_count(1)
        expect(section.locator("img").first).to_have_js_property("naturalWidth", 160)
        expect(section.get_by_text("seconde.jpg", exact=True)).to_be_visible()
        expect(section.get_by_text("Flou possible", exact=False)).to_be_visible()
        dav(owner, "DELETE", base+"prise.jpg", [412], **{"If-Match": '"version-obsolete"'})
        empty = login(browser, other)
        expect(empty.locator(".serie")).to_have_count(0)
        check = section.locator("figure").filter(has_text="prise-copie.jpg").get_by_role("checkbox")
        check.check()
        page.once("dialog", lambda dialog: dialog.accept())
        section.locator(".discard").click()
        expect(page.get_by_text("prise-copie.jpg", exact=True)).to_have_count(0)
        dav(owner, "GET", base+"prise-copie.jpg", [404])
        assert b"prise-copie.jpg" in dav(owner, "PROPFIND", f"/remote.php/dav/trashbin/{owner}/trash/", [207], Depth="1")
        remaining = page.locator(".serie").first
        expect(remaining.get_by_text("À conserver en priorité", exact=False)).to_be_visible()
        remaining.locator(".ignore").click()
        expect(remaining).to_have_count(0)
        browser.close()
    print("OK · galerie privée, aperçu, corbeille et suggestion ignorée")


if __name__ == "__main__":
    try:
        test_review()
    finally:
        for user in reversed(members):
            occ("user:delete", user)
