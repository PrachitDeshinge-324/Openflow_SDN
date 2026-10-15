#!/usr/bin/env bash
# Downloads the freely available papers cited in Literature_Review_IdleHybrid.md
# into docs/literature/papers/ (that folder is git-ignored: the PDFs are the
# publishers' copyright, so they stay on your laptop and are not pushed to the
# public repo).
#
# Usage, from the repository root:
#   bash docs/literature/download_papers.sh
#
# Papers behind a paywall (PARD, the IEEE hybrid-placement paper, the 2025
# Cluster Computing paper) are not downloaded: open their DOI links from the
# review through the BITS library / institutional access.

set -u
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/papers"
mkdir -p "$DIR"

PAPERS=(
  "2007_Casado_Ethane_SIGCOMM.pdf|https://yuba.stanford.edu/~nickm/papers/ethane-sigcomm07.pdf"
  "2010_Yu_DIFANE_SIGCOMM.pdf|https://www.cs.princeton.edu/~jrex/papers/difane10.pdf"
  "2010_Benson_DC_Traffic_IMC.pdf|https://conferences.sigcomm.org/imc/2010/papers/p267.pdf"
  "2011_Curtis_DevoFlow_SIGCOMM.pdf|https://conferences.sigcomm.org/sigcomm/2011/papers/sigcomm/p254.pdf"
  "2012_Tootoonchian_ControllerPerf_HotICE.pdf|https://www.usenix.org/system/files/conference/hot-ice12/hotice12-final33_0.pdf"
  "2012_HassasYeganeh_Kandoo_HotSDN.pdf|https://www.cs.princeton.edu/courses/archive/fall13/cos597E/papers/kandoo.pdf"
  "2014_Vishnoi_SmartTime_DEBS.pdf|https://rishabhpoddar.com/publications/SmartTime.pdf"
  "2016_Katta_CacheFlow_SOSR.pdf|https://www.cs.princeton.edu/~jrex/papers/cacheflow16.pdf"
  "2020_Isyaku_AH-IHTA_Electronics.pdf|https://www.mdpi.com/2079-9292/9/11/1983/pdf"
  "2022_Kim_MobilityAwareHybridCache_Electronics.pdf|https://www.mdpi.com/2079-9292/11/1/160/pdf"
  "2024_Batista_LSTMScheduler_DiscoverIoT.pdf|https://repositum.tuwien.at/bitstream/20.500.12708/202598/1/Batista-2024-Discover%20Internet%20of%20Things-vor.pdf"
)

ok=0; fail=0
for entry in "${PAPERS[@]}"; do
  name="${entry%%|*}"; url="${entry#*|}"
  if [ -s "$DIR/$name" ]; then
    echo "  have  $name"; ok=$((ok + 1)); continue
  fi
  if curl -fsSL --max-time 90 -A "Mozilla/5.0" -o "$DIR/$name.part" "$url" \
     && head -c 5 "$DIR/$name.part" | grep -q '%PDF'; then
    mv "$DIR/$name.part" "$DIR/$name"; echo "  got   $name"; ok=$((ok + 1))
  else
    rm -f "$DIR/$name.part"; echo "  FAIL  $name  <- open in a browser: $url"; fail=$((fail + 1))
  fi
done
echo "Done: $ok downloaded or present, $fail failed. Files in $DIR"
