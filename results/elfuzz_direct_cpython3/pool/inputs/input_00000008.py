"""
    Problem: 18. 4Sum

    Given an array nums of n integers and an integer target, are there elements a, b, c, and d in nums such that a + b + c + d = target? Find all unique quadruplets in the array which gives the sum of target.
    Notice that the solution set must not contain duplicate quadruplets.

    Example 1:
        Input: nums = [1,0,-1,0,-2,2], target = 0
        Output: [[-2,-1,1,2],[-2,0,0,2],[-1,0,0,1]]

    Example 2:
        Input: nums = [], target = 0
        Output: []

    Constraints:
        * 0 <= nums.length <= 200
        * -109 <= nums[i] <= 109
        * -109 <= target <= 109
"""
from typing import List


class Solution:
    def fourSum(self, nums: List[int], target: int) -> List[List[int]]:

        result = []
        nums.sort()

        for i in range(len(nums)):
            if i > 0 and nums[i] == nums[i - 1]: continue
            for j in range(i+1,len(nums)):
                if j>i+1 and nums[j]==nums[j-1]:continue
                left=j+1
                right=len(nums)-1
                while(left<right):
                    sum=nums[i]+nums[j]+nums[left]+nums[right]
                    if sum==target:
                        temp=[nums[i],nums[j],nums[left],nums[right]]
                        result.append(temp)
                        left+=1
                        right-=1
                        while left < right and nums[left] == nums[left - 1]:
                            left += 1
                        while left < right and nums[right] == nums[right + 1]:
                            right -= 1
                    elif sum>target:right-=1
                    else:left+=1
        
        return result