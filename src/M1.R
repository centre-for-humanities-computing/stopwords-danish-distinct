library(rvest)
library(tidyverse)
library(textcat)
library(cld2)
library(cld3)

wiki = read_html("https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Danish_wordlist")

da_common = wiki %>%
  rvest::html_nodes("ol") %>%
  rvest::html_nodes("li") %>%
  rvest::html_text() %>%
  tibble::enframe(name = "rank", value = "ww") %>%
  tidyr::separate(ww, into = c('word', 'count'), sep = " ") %>%
  dplyr::mutate(textcat = textcat::textcat(word),
                cld2 = cld2::detect_language(word),
                cld3 = cld3::detect_language(word)) 

contains_da = da_common %>%
  dplyr::filter(textcat == "danish" | cld2 == "da" | cld3 == "da")

distinctly_da = da_common %>%
  dplyr::filter(textcat == "danish" & cld3 == "da") %>%
  dplyr::select(word, count)

write_csv(distinctly_da, "../M1_distinctly_da.csv")
write_lines(distinctly_da$word, "../M1_distinctly_da.txt")
