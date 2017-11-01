# Price Feed Script for BitShares

## Installation 

Ubuntu 16.04 LTS

```
cd ~
sudo apt install python3-pip
pip3 install --upgrade pip
pip3 install bitshares-pricefeed
bitshares-pricefeed create
uptick addkey
```

You will need to enter your cli wallet encryption passphrase here:

```
Wallet Encryption Passphrase:
Repeat for confirmation:
```

You will need to enter your Private Key (Active key) here. Hit enter the second time it asks you.

```
Private Key (wif) [Enter to quit]:
```

Manually run the feed update

```
bitshares-pricefeed update
```

Add to cron, where PASSWD is your Wallet Encryption Passphrase

```
UNLOCK="PASSWD" bitshares-pricefeed update
```

# IMPORTANT NOTE

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
