#!/usr/bin/env python3

import prepare_data
import check_outliers
import review_manually_fixed
import find_matching
import output_matched_data

prepare_data.main()
check_outliers.main()
review_manually_fixed.main()
find_matching.main()
output_matched_data.main()

