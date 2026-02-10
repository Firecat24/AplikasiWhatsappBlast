/*************************************************************************
* ADOBE CONFIDENTIAL
* ___________________
*
*  Copyright 2015 Adobe Systems Incorporated
*  All Rights Reserved.
*
* NOTICE:  All information contained herein is, and remains
* the property of Adobe Systems Incorporated and its suppliers,
* if any.  The intellectual and technical concepts contained
* herein are proprietary to Adobe Systems Incorporated and its
* suppliers and are protected by all applicable intellectual property laws,
* including trade secret and or copyright laws.
* Dissemination of this information or reproduction of this material
* is strictly forbidden unless prior written permission is obtained
* from Adobe Systems Incorporated.
**************************************************************************/
import{loggingApi as t}from"../common/loggingApi.js";import e from"./CacheStore.js";import{floodgate as i}from"./floodgate.js";import{dcLocalStorage as o}from"../common/local-storage.js";import{isAddWebpageToProjectEnabled as r}from"./add-webpage-to-project.js";import{forceResetService as s}from"./force-reset-service.js";import{common as a}from"./common.js";const c=new class{constructor(){this.THIRTY_DAYS=2592e6,this.promise=null}async fetch(t){const e=await fetch(t);if(!e.ok)throw new Error(`Failed to fetch block list from ${t}: ${e.statusText}`);return(await e.text()).split("\n").map((t=>t.trim())).filter((t=>t.length>0))}async _get({blockListUrl:i,cacheKey:o,featureName:r}){const a=new e("explicit-blocklist");try{const t=async()=>{const t=await this.fetch(i);return t?.length>0&&await a.set(o,t),t||[]},{executionResult:e}=await s.executeFeature(r,t);if(e?.length>0)return e}catch(e){t.error({message:"Error fetching explicit block list from Adobe",error:e.toString(),blockListUrl:i})}return await a.get(o)||[]}async _getExplicitBlocklist(){await o.init();if(!await i.hasFlag("dc-cv-domain-moderation-enabled"))return[];const t={cacheKey:"explicitBlockList",blockListUrl:a.getModerationListUrl(),featureName:"common-moderation-list"};return await this._get(t)}async _getKWBlockList(){await o.init();const t=await i.hasFlag("dc-cv-kw-domain-moderation-enabled"),e=await r();if(!t||!e)return[];const s={cacheKey:"explicitBlockList-kw",blockListUrl:a.getKWModerationListUrl(),featureName:"kw-moderation-list"};return await this._get(s)}async getExplicitBlocklist(){return this.promise||(this.promise=this._getExplicitBlocklist()),this.promise}async getKWBlockList(){return this.kwPromise||(this.kwPromise=this._getKWBlockList()),this.kwPromise}};export default c;