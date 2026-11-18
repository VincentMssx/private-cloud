"""Essai du panneau sur un membre et un administrateur temporaire avec TOTP."""
import base64
import hashlib
import hmac
import os
import secrets
import shutil
import struct
import time

from playwright.sync_api import expect, sync_playwright
from parcours import BASE, ROOT, dav, occ, password
from tri import login


def otp(secret, counter):
    digest = hmac.new(base64.b32decode(secret), struct.pack(">Q", counter), hashlib.sha1).digest()
    start = digest[-1] & 15
    return f"{(int.from_bytes(digest[start:start+4], 'big') & 0x7fffffff) % 1000000:06d}"


def post(page, url, params):
    return page.evaluate("""async ([path, params]) => {
        const response = await fetch(path, {method: 'POST', headers: {requesttoken: OC.requestToken},
            body: new URLSearchParams(params)})
        return {code: response.status, data: await response.json().catch(() => null)}
    }""", [url, params])


def run(owner, manager):
    quota_path = "/apps/familytri/admin/quota"
    folder = f"/remote.php/dav/files/{owner}/"
    dav(owner, "MKCOL", folder + "Essai", [201])
    dav(owner, "PUT", folder + "Essai/image.jpg", [201], (ROOT/"tests/mire.jpg").read_bytes())
    dav(owner, "PUT", folder + "note.txt", [201], b"hello")
    dav(owner, "PUT", folder + "archive.txt", [201], bytes(1024))
    dav(owner, "DELETE", folder + "archive.txt", [204])
    occ("memories:index", "--user", owner)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.getenv("CHROME_BIN") or shutil.which("chromium") or shutil.which("google-chrome"))
        member = login(browser, owner)
        assert post(member, quota_path, {"uid": owner, "amount": "1", "unit": "MB"})["code"] in (401, 403)
        member.goto(BASE + "/settings/admin/familytri")
        expect(member.locator("#family-admin")).to_have_count(0)

        setup = login(browser, manager)
        endpoint = "/apps/twofactor_totp/settings/enable"
        result = post(setup, endpoint, {"state": "1"})
        assert result["code"] == 200 and "secret" in result["data"]
        key = result["data"]["secret"]
        tick = int(time.time()) // 30
        assert post(setup, endpoint, {"state": "2", "code": otp(key, tick)})["data"]["state"] == 2
        setup.context.close()
        occ("group:adduser", "admin", manager)
        page = browser.new_page()
        page.goto(BASE + "/login")
        page.locator("input[name=user]").fill(manager)
        page.locator("input[type=password]").fill(password)
        page.locator("input[type=password]").press("Enter")
        page.wait_for_url("**/login/**")
        page.goto(BASE + "/login/challenge/totp")
        field = page.locator("input[name=challenge]")
        expect(field).to_be_visible()
        time.sleep(max(0, (tick + 1) * 30 + 1 - time.time()))
        field.fill(otp(key, int(time.time()) // 30))
        field.press("Enter")
        page.wait_for_url("**/apps/**")
        page.goto(BASE + "/settings/admin/familytri")
        card = page.locator(f".family-account[data-user='{owner}']")
        expect(card.locator('[data-metric=files]')).to_have_text("2")
        expect(card.locator('[data-metric=photos]')).to_have_text("1")
        assert card.locator('[data-metric=trash]').inner_text() not in ("0 B", "0")
        assert int(card.locator('[data-metric=pending]').inner_text()) in (0, 1)
        assert post(page, quota_path, {"uid": owner, "amount": "-1", "unit": "MB"})["code"] == 400
        card.locator("summary").click()
        card.locator("select").select_option("MB")
        card.locator("input[name=amount]").fill("1")
        card.locator("button[type=submit]").click()
        expect(card.locator('[role=status]')).to_have_text("Quota enregistré.")
        dav(owner, "PUT", folder + "limite.bin", [507], bytes(2 * 1024 * 1024))
        page.reload()
        expect(card.locator('[data-metric=quota]')).to_contain_text("1 MB")
        browser.close()
    print("OK · statistiques par compte, refus pour un membre, connexion admin TOTP et quota effectif")


if __name__ == "__main__":
    users = []
    try:
        for _ in range(2):
            user = "panneau-" + secrets.token_hex(5)
            occ("user:add", "--password-from-env", user, create=True)
            users.append(user)
        run(*users)
    finally:
        for user in reversed(users):
            occ("user:delete", user)
