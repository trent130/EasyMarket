'use client';

import React from 'react';
import type { ProductSearchFilters, Category } from '../../types/product';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { RadioGroup, RadioGroupItem } from '../ui/radio-group';
import { Checkbox } from '../ui/checkbox';

interface ProductFilterProps {
    filters: ProductSearchFilters;
    categories: Category[];
    onChange: (filters: Partial<ProductSearchFilters>) => void;
}

export default function ProductFilter({ filters, categories, onChange }: ProductFilterProps) {
    const conditions = [
        { value: 'new', label: 'New' },
        { value: 'like_new', label: 'Like New' },
        { value: 'good', label: 'Good' },
        { value: 'fair', label: 'Fair' },
    ];

    return (
        <div className="space-y-6">
            {/* Price Range */}
            <div className="space-y-2">
                <Label>Price Range</Label>
                <div className="flex items-center gap-2">
                    <Input
                        type="number"
                        placeholder="Min"
                        value={filters.min_price || ''}
                        onChange={(e) => onChange({ min_price: Number(e.target.value) || undefined })}
                        className="w-24"
                    />
                    <span>to</span>
                    <Input
                        type="number"
                        placeholder="Max"
                        value={filters.max_price || ''}
                        onChange={(e) => onChange({ max_price: Number(e.target.value) || undefined })}
                        className="w-24"
                    />
                </div>
            </div>

            {/* Categories */}
            <div className="space-y-2">
                <Label>Categories</Label>
                <div className="grid grid-cols-2 gap-2">
                    {categories.map((category) => (
                        <Button
                            key={category.id}
                            variant={filters.category === category.id ? 'default' : 'outline'}
                            onClick={() => onChange({
                                category: filters.category === category.id ? undefined : category.id
                            })}
                            className="justify-start"
                        >
                            {category.name}
                            {category.product_count > 0 && (
                                <span className="ml-auto text-xs text-muted-foreground">
                                    ({category.product_count})
                                </span>
                            )}
                        </Button>
                    ))}
                </div>
            </div>

            {/* Condition */}
            <div className="space-y-2">
                <Label>Condition</Label>
                <RadioGroup
                    value={filters.condition || ''}
                    onValueChange={(value) => onChange({ condition: value as any || undefined })}
                >
                    {conditions.map((condition) => (
                        <div key={condition.value} className="flex items-center space-x-2">
                            <RadioGroupItem value={condition.value} id={condition.value} />
                            <Label htmlFor={condition.value}>{condition.label}</Label>
                        </div>
                    ))}
                </RadioGroup>
            </div>

            {/* Stock Status */}
            <div className="flex items-center space-x-2">
                <Checkbox
                    id="in_stock"
                    checked={filters.in_stock}
                    onCheckedChange={(checked) => onChange({ in_stock: checked as boolean })}
                />
                <Label htmlFor="in_stock">In Stock Only</Label>
            </div>

            {/* Clear Filters */}
            <Button
                variant="outline"
                className="w-full"
                onClick={() => onChange({
                    category: undefined,
                    min_price: undefined,
                    max_price: undefined,
                    condition: undefined,
                    in_stock: undefined,
                })}
            >
                Clear Filters
            </Button>
        </div>
    );
}
