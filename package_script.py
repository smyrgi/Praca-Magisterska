#!/usr/bin/env python3

import prepare_data
import check_outliers
import review_manually_fixed
import find_matching

prepare_data.main()
check_outliers.main()
review_manually_fixed.main()
find_matching.main()

